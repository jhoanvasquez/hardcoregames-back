from django.urls import path

from products import views

urlpatterns = [
    path("createProduct/", views.create_product, name="create_product"),
    path("createSale/", views.create_sale, name="create_sale"),
    path("getAllProducts/", views.get_all_products, name="get_all_products"),
    path("getFavProducts/", views.get_favorite_products, name="get_favorite_products"),
    path("getNewsProducts/", views.get_news_for_products, name="get_news_for_products"),
    path("getProductById/<int:id_product>", views.get_products_by_id, name="get_products_by_id"),
    path("getProductByTypeGame/<int:id_type_game>", views.get_products_by_type_game, name="get_products_by_type_game"),
    path("getProductByTypeConsole/<int:id_console>", views.get_products_by_type_console, name="get_products_by_id"),
    path("getLicensces/", views.get_licences, name="get_products_by_id"),
    path("getConsoles/", views.get_consoles, name="get_products_by_id"),
    path("getTypeGames/", views.get_type_games, name="get_type_games"),
    path("getShoppingCar/", views.get_shopping_car, name="get_shopping_car"),
    path("updateShoppingCar/<int:shooping_car_id>", views.update_shopping_car, name="update_shopping_car"),
    path("deleteShoppingCar/<int:shooping_car_id>", views.delete_product_shopping_car, name="delete_shopping_car"),
    path("shoppingCar/", views.shopping_car, name="shopping_car"),
    path("sendEmail/", views.sendEmail, name="sendEmail"),
]