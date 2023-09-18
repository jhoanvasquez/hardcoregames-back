from django.urls import path

from products import views

urlpatterns = [
    path("createProduct/", views.create_product, name="create_product"),
]