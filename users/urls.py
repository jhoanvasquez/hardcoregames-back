from django.urls import path, include
from users import views

urlpatterns = [
    path("/", views.get_all_users, name=""),
    path("/<int:question_id>/", views.detail, name="detail"),
]
