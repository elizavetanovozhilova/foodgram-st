from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Value
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from djoser.conf import settings
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthor
from api.serializers import (CustomUserSerializer, FavoriteSerializer,
                             FollowSerializer, IngredientRecipe,
                             IngredientSerializer, RecipeSerializer,
                             RecipeWriteSerializer, ShoppingCardSerializer,
                             TagSerializer)
from api.viewsets import ListRetriveViewSet, ListViewSet
from recipes.models import (Favorite, Follow, Ingredient, Recipe, ShoppingList,
                            Tag)

User = get_user_model()


class IngredientViewSet(ListRetriveViewSet):
    """Ингредиенты."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = IngredientFilter


class TagViewSet(ListRetriveViewSet):
    """Теги."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class CustomUserViewSet(UserViewSet):
    """Пользователи."""

    serializer_class = CustomUserSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_context(self):
        """Получить контекст."""
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_serializer_class(self):
        """Получить сериализатор."""
        if self.action == "create":
            if settings.USER_CREATE_PASSWORD_RETYPE:
                return settings.SERIALIZERS.user_create_password_retype
            return settings.SERIALIZERS.user_create
        if self.action == "set_password":
            if settings.SET_PASSWORD_RETYPE:
                return settings.SERIALIZERS.set_password_retype
            return settings.SERIALIZERS.set_password
        return self.serializer_class

    @action(["get"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(["put"], detail=False, permission_classes=[IsAuthenticated])
    def avatar(self, request, *args, **kwargs):
        """Загрузить аватар."""
        user = request.user
        if 'avatar' in request.data:
            # Handle base64 image data
            avatar_data = request.data['avatar']
            if isinstance(avatar_data, str) and avatar_data.startswith('data:image'):
                # Extract the base64 data
                format, imgstr = avatar_data.split(';base64,')
                ext = format.split('/')[-1]
                
                # Create a ContentFile from the base64 data
                from django.core.files.base import ContentFile
                import base64
                data = ContentFile(base64.b64decode(imgstr), name=f'avatar.{ext}')
                user.avatar = data
            else:
                user.avatar = avatar_data
            user.save()
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        return Response(
            {'error': 'Avatar field is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(["delete"], detail=False, permission_classes=[IsAuthenticated])
    def avatar_delete(self, request, *args, **kwargs):
        """Удалить аватар."""
        user = request.user
        if user.avatar:
            user.avatar.delete()
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепты."""

    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    ordering = ('-pub_date',)

    def get_queryset(self):
        """Получить кверисет."""
        user = self.request.user
        if user.is_authenticated:
            return Recipe.objects.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(user=user, recipe=OuterRef('pk'))
                ),
                is_in_shopping_cart=Exists(
                    ShoppingList.objects.filter(user=user,
                                                recipe=OuterRef('pk'))
                )
            ).all()
        return Recipe.objects.annotate(
            is_favorited=Value(False),
            is_in_shopping_cart=Value(False)
        ).all()

    def get_serializer_class(self):
        """Получить сериализатор."""
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeWriteSerializer

    def get_permissions(self):
        """Проверка доступа."""
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.AllowAny(),)
        return (permissions.IsAuthenticated(), IsAuthor(),)

    def perform_create(self, serializer):
        """Добавить автора."""
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        """Получить контекст."""
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class ListSubscribeViewSet(ListViewSet):
    """Список подписок пользователя."""
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    ordering = ('id',)

    def get_queryset(self):
        """Получить кверисет."""
        user = self.request.user
        return user.follower.all()

    def get_serializer_context(self):
        """Получить контекст."""
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def favorite(request, recipe_id):
    """Добавить/удалить из избранного"""
    if request.method == "POST":
        serializer = FavoriteSerializer(
            data=request.data,
            context={'request': request, 'recipe_id': recipe_id}
        )
        serializer.is_valid(raise_exception=True)
        recipe = get_object_or_404(Recipe, id=recipe_id)
        serializer.save(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    serializer = FavoriteSerializer(
        data=request.data,
        context={'request': request, 'recipe_id': recipe_id}
    )
    serializer.is_valid(raise_exception=True)
    Favorite.objects.filter(
        user=request.user,
        recipe=get_object_or_404(Recipe, id=recipe_id)
    ).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def subscribe(request, user_id):
    """Добавить/удалить подписку."""
    try:
        following = get_object_or_404(User, id=user_id)
    except Exception:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "POST":
        serializer = FollowSerializer(
            data=request.data,
            context={'request': request, 'user_id': user_id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, following=following)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    serializer = FollowSerializer(
        data=request.data,
        context={'request': request, 'user_id': user_id}
    )
    serializer.is_valid(raise_exception=True)
    Follow.objects.filter(
        user=request.user,
        following=following
    ).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def shopping(request, recipe_id):
    """Добавить/удалить покупку."""
    if request.method == "POST":
        serializer = ShoppingCardSerializer(
            data=request.data,
            context={'request': request, 'recipe_id': recipe_id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user,
                        recipe=get_object_or_404(Recipe, id=recipe_id))
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    serializer = ShoppingCardSerializer(
        data=request.data,
        context={'request': request, 'recipe_id': recipe_id}
    )
    serializer.is_valid(raise_exception=True)
    ShoppingList.objects.filter(
        user=request.user,
        recipe=get_object_or_404(Recipe, id=recipe_id)
    ).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def download_shopping_cart(request):
    """Скачать список покупок."""
    ingredients = IngredientRecipe.objects.filter(
        recipe__shopping_recipe__user=request.user
    )
    shopping_data = {}
    for ingredient in ingredients:
        if str(ingredient.ingredient) in shopping_data:
            shopping_data[f'{str(ingredient.ingredient)}'] += ingredient.amount
        else:
            shopping_data[f'{str(ingredient.ingredient)}'] = ingredient.amount
    filename = "shopping-list.txt"
    content = ''
    for ingredient, amount in shopping_data.items():
        content += f"{ingredient} - {amount};\n"
    response = HttpResponse(content, content_type='text/plain',
                            status=status.HTTP_200_OK)
    response['Content-Disposition'] = 'attachment; filename={0}'.format(
        filename)
    return response


@api_view(["GET"])
def get_recipe_short_link(request, recipe_id):
    """Получить короткую ссылку на рецепт."""
    recipe = get_object_or_404(Recipe, id=recipe_id)
    # Создаем короткую ссылку на основе ID рецепта
    short_link = f"https://localhost/recipes/{recipe.id}"
    return Response({"short-link": short_link})



@api_view(["GET"])
def advanced_recipe_filter(request):
    search = request.query_params.get('search', '')
    min_cooking_time = request.query_params.get('min_cooking_time')
    max_cooking_time = request.query_params.get('max_cooking_time')
    min_ingredients = request.query_params.get('min_ingredients')
    max_ingredients = request.query_params.get('max_ingredients')
    author_username = request.query_params.get('author_username')
    tags = request.query_params.getlist('tags')
    sort_by = request.query_params.get('sort_by', 'pub_date')
    order = request.query_params.get('order', 'desc')

    queryset = Recipe.objects.select_related('author').prefetch_related('tags', 'ingredients')

    if search:
        queryset = queryset.filter(Q(name__icontains=search) | Q(text__icontains=search))
    if min_cooking_time:
        queryset = queryset.filter(cooking_time__gte=min_cooking_time)
    if max_cooking_time:
        queryset = queryset.filter(cooking_time__lte=max_cooking_time)
    if min_ingredients:
        queryset = queryset.annotate(ingredient_count=Count('ingredients')).filter(ingredient_count__gte=min_ingredients)
    if max_ingredients:
        queryset = queryset.annotate(ingredient_count=Count('ingredients')).filter(ingredient_count__lte=max_ingredients)
    if author_username:
        queryset = queryset.filter(author__username__icontains=author_username)
    if tags:
        queryset = queryset.filter(tags__slug__in=tags).distinct()

    if sort_by == 'popularity':
        queryset = queryset.annotate(favorite_count=Count('favorite_recipe')).order_by(f'-favorite_count' if order == 'desc' else 'favorite_count')
    elif sort_by == 'name':
        queryset = queryset.order_by(f'-name' if order == 'desc' else 'name')
    elif sort_by == 'cooking_time':
        queryset = queryset.order_by(f'-cooking_time' if order == 'desc' else 'cooking_time')
    else:
        queryset = queryset.order_by(f'-pub_date' if order == 'desc' else 'pub_date')

    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 10))
    offset = (page - 1) * limit

    total_count = queryset.count()
    recipes = queryset[offset:offset + limit]
    serializer = RecipeSerializer(recipes, many=True, context={'request': request})

    return Response({
        'count': total_count,
        'next': f'?page={page + 1}' if offset + limit < total_count else None,
        'previous': f'?page={page - 1}' if page > 1 else None,
        'results': serializer.data,
        'filters_applied': {
            'search': search,
            'min_cooking_time': min_cooking_time,
            'max_cooking_time': max_cooking_time,
            'min_ingredients': min_ingredients,
            'max_ingredients': max_ingredients,
            'author_username': author_username,
            'tags': tags,
            'sort_by': sort_by,
            'order': order
        }
    })

@api_view(["GET"])
def user_profile_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    recipes_count = user.recipes.count()
    followers_count = user.following.count()
    following_count = user.follower.count()
    recent_recipes = user.recipes.order_by('-pub_date')[:5]
    recent_recipes_serializer = RecipeSerializer(recent_recipes, many=True, context={'request': request})
    popular_recipes = user.recipes.annotate(favorite_count=Count('favorite_recipe')).order_by('-favorite_count')[:5]
    popular_recipes_serializer = RecipeSerializer(popular_recipes, many=True, context={'request': request})
    is_subscribed = False
    if request.user.is_authenticated:
        is_subscribed = user.follower.filter(user=request.user).exists()
    user_serializer = CustomUserSerializer(user, context={'request': request})
    return Response({
        'user': user_serializer.data,
        'statistics': {
            'recipes_count': recipes_count,
            'followers_count': followers_count,
            'following_count': following_count,
            'is_subscribed': is_subscribed
        },
        'recent_recipes': recent_recipes_serializer.data,
        'popular_recipes': popular_recipes_serializer.data
    })

@api_view(["GET"])
def recipe_statistics(request):
    total_recipes = Recipe.objects.count()
    total_users = User.objects.count()
    total_favorites = Favorite.objects.count()
    total_shopping_lists = ShoppingList.objects.count()
    from django.utils import timezone
    from datetime import timedelta
    week_ago = timezone.now() - timedelta(days=7)
    new_recipes_week = Recipe.objects.filter(pub_date__gte=week_ago).count()
    new_users_week = User.objects.filter(date_joined__gte=week_ago).count()
    popular_recipes = Recipe.objects.annotate(favorite_count=Count('favorite_recipe')).order_by('-favorite_count')[:10]
    popular_recipes_serializer = RecipeSerializer(popular_recipes, many=True, context={'request': request})
    recent_recipes = Recipe.objects.order_by('-pub_date')[:10]
    recent_recipes_serializer = RecipeSerializer(recent_recipes, many=True, context={'request': request})
    tag_stats = Tag.objects.annotate(recipe_count=Count('recipe')).order_by('-recipe_count')[:10]
    author_stats = User.objects.annotate(
        recipe_count=Count('recipes'),
        total_favorites=Count('recipes__favorite_recipe')
    ).filter(recipe_count__gt=0).order_by('-recipe_count')[:10]
    avg_cooking_time = Recipe.objects.aggregate(Avg('cooking_time'))['cooking_time__avg']
    avg_ingredients_per_recipe = Recipe.objects.annotate(
        ingredient_count=Count('ingredients')
    ).aggregate(Avg('ingredient_count'))['ingredient_count__avg']
    return Response({
        'overall_statistics': {
            'total_recipes': total_recipes,
            'total_users': total_users,
            'total_favorites': total_favorites,
            'total_shopping_lists': total_shopping_lists,
            'new_recipes_week': new_recipes_week,
            'new_users_week': new_users_week,
            'avg_cooking_time': round(avg_cooking_time, 1) if avg_cooking_time else 0,
            'avg_ingredients_per_recipe': round(avg_ingredients_per_recipe, 1) if avg_ingredients_per_recipe else 0
        },
        'popular_recipes': popular_recipes_serializer.data,
        'recent_recipes': recent_recipes_serializer.data,
        'top_tags': [
            {
                'id': tag.id,
                'name': tag.name,
                'color': tag.color,
                'slug': tag.slug,
                'recipe_count': tag.recipe_count
            }
            for tag in tag_stats
        ],
        'top_authors': [
            {
                'id': author.id,
                'username': author.username,
                'first_name': author.first_name,
                'last_name': author.last_name,
                'recipe_count': author.recipe_count,
                'total_favorites': author.total_favorites
            }
            for author in author_stats
        ]
    })