apiVersion: v1
kind: ConfigMap
metadata:
  name: locustfile
  namespace: foodgram
data:
  locustfile.py: |
    from locust import HttpUser, task, between

    class FoodgramUser(HttpUser):
        wait_time = between(1, 3)

        @task
        def get_recipes(self):
            self.client.get("/api/recipes/")

        @task
        def get_tags(self):
            self.client.get("/api/tags/")

        @task
        def get_ingredients(self):
            self.client.get("/api/ingredients/")