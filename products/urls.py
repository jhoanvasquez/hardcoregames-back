from django.urls import path

from products import views

urlpatterns = [
    path("createProduct/", views.create_product, name="create_product"),
    path("getAllProducts/", views.get_all_products, name="get_all_products"),
    path("getFavProducts/", views.get_favorite_products, name="get_favorite_products"),
    path("getNewsProducts/", views.get_news_for_products, name="get_news_for_products"),
]