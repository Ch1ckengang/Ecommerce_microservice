from django.urls import path

from .views import ProfileView, RegisterView, UserTokenObtainPairView, UserTokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="user-register"),
    path("token/", UserTokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", UserTokenRefreshView.as_view(), name="token-refresh"),
    path("me/", ProfileView.as_view(), name="user-profile"),
]
