from django.urls import path

from posts.views import (
    CreatePostView,
    FacebookCallbackView,
    FacebookLoginView,
    InstagramCallbackView,
    InstagramLoginView,
    ManageAccountsView,
    TwitterCallbackView,
    TwitterLoginView,
)

urlpatterns = [
    path("create/", CreatePostView.as_view(), name="create_post"),
    path("accounts/", ManageAccountsView.as_view(), name="manage_accounts"),
    path("twitter/login/", TwitterLoginView.as_view(), name="twitter_login"),
    path("twitter/callback/", TwitterCallbackView.as_view(), name="twitter_callback"),
    path("facebook/login/", FacebookLoginView.as_view(), name="facebook_login"),
    path(
        "facebook/callback/", FacebookCallbackView.as_view(), name="facebook_callback"
    ),
    path("instagram/login/", InstagramLoginView.as_view(), name="instagram_login"),
    path(
        "instagram/callback/",
        InstagramCallbackView.as_view(),
        name="instagram_callback",
    ),
]
