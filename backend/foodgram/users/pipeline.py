from django.conf import settings
from rest_framework.authtoken.models import Token
from django.shortcuts import redirect

import logging

def redirect_with_token(strategy, backend, user=None, *args, **kwargs):
    logging.warning(f"REDIRECT PIPELINE: user={user}")
    if user is None:
        return
    token, _ = Token.objects.get_or_create(user=user)
    frontend_url = settings.SOCIAL_AUTH_REDIRECT_URL or 'http://localhost'
    url = f"{frontend_url}/?token={token.key}"
    logging.warning(f"REDIRECT TO: {url}")
    return redirect(url)