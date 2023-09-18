from django.urls import path
from users import views

urlpatterns = [
    path("", views.get_all_users, name=""),
    path("index/", views.index, name="index"),
    path("login/", views.login_request, name="login"),
    path("logout/", views.logout_request, name="login"),
    path("register/", views.register, name="register"),
    path("findUserByEmail/", views.get_user_by_email, name="find_user_by_email"),
    path("findUserById/<int:id_user>", views.get_user_by_id, name="find_user_by_id"),
]
