from django.urls import path, include
from . import views

app_name = "travel"

urlpatterns = [
    path("", views.home, name="home"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("protected/", views.protected, name="protected"),
     # 景点详情
    path("attractions/<int:attraction_id>/", views.attraction_detail, name="attraction_detail"),
    # 收藏切换
    path("attractions/<int:attraction_id>/bookmark/", views.toggle_bookmark, name="toggle_bookmark"),
    # 收藏列表
    path("bookmarks/", views.bookmarks, name="bookmarks"),
]