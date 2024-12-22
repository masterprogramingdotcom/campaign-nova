import os

import requests
import tweepy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from requests_oauthlib import OAuth1Session

from CampaignNova.settings import base as settings
from posts.models import Post, SocialMediaAccount

# Centralized constants
TWITTER_REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
TWITTER_AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize"
TWITTER_ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"
FACEBOOK_OAUTH_URL = "https://www.facebook.com/v14.0/dialog/oauth"
FACEBOOK_ACCESS_TOKEN_URL = "https://graph.facebook.com/v14.0/oauth/access_token"
INSTAGRAM_OAUTH_URL = "https://api.instagram.com/oauth/authorize"
INSTAGRAM_ACCESS_TOKEN_URL = "https://api.instagram.com/oauth/access_token"


# Helper function to handle API errors
def handle_api_response(response):
    if response.status_code != 200:
        return {"error": "Failed to connect to the API."}
    return response.json()


# Helper function to save social media account tokens
def save_social_account(user, platform, token):
    account, _ = SocialMediaAccount.objects.get_or_create(user=user)
    setattr(account, platform, token)
    account.save()


class InstagramLoginView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        redirect_uri = f"{settings.DOMAIN_NAME}/dashboard/posts/instagram/callback/"
        url = (
            f"{INSTAGRAM_OAUTH_URL}?client_id={settings.INSTAGRAM_CLIENT_ID}"
            f"&redirect_uri={redirect_uri}&response_type=code&scope=user_profile"
        )
        return redirect(url)


class InstagramCallbackView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")
        if not code:
            return JsonResponse({"error": "Authorization failed."}, status=400)
        redirect_uri = f"{settings.DOMAIN_NAME}/dashboard/posts/instagram/callback/"
        response = requests.post(
            INSTAGRAM_ACCESS_TOKEN_URL,
            data={
                "client_id": settings.INSTAGRAM_CLIENT_ID,
                "client_secret": settings.INSTAGRAM_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
                "code": code,
            },
        )
        data = handle_api_response(response)
        if "error" in data:
            return JsonResponse(data, status=400)
        save_social_account(request.user, "instagram", data["access_token"])
        return redirect("manage_accounts")


class FacebookLoginView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        redirect_uri = f"{settings.DOMAIN_NAME}/dashboard/posts/facebook/callback/"
        url = (
            f"{FACEBOOK_OAUTH_URL}?client_id={settings.FACEBOOK_APP_ID}"
            f"&redirect_uri={redirect_uri}&state={request.user.id}&scope=email,public_profile"
        )
        return redirect(url)


class FacebookCallbackView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")
        if not code:
            return JsonResponse({"error": "Authorization failed."}, status=400)
        redirect_uri = f"{settings.DOMAIN_NAME}/dashboard/posts/facebook/callback/"
        response = requests.get(
            f"{FACEBOOK_ACCESS_TOKEN_URL}?client_id={settings.FACEBOOK_APP_ID}"
            f"&redirect_uri={redirect_uri}&client_secret={settings.FACEBOOK_APP_SECRET}&code={code}"
        )
        data = handle_api_response(response)
        if "error" in data:
            return JsonResponse(data, status=400)
        save_social_account(request.user, "facebook", data["access_token"])
        return redirect("manage_accounts")


class TwitterLoginView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Step 1: Get a request token from Twitter
        oauth = OAuth1Session(
            settings.TWITTER_API_KEY,
            client_secret=settings.TWITTER_API_SECRET_KEY,
            callback_uri=f"{settings.DOMAIN_NAME}/dashboard/posts/twitter/callback/",
        )

        try:
            # Request an OAuth request token
            data = oauth.fetch_request_token(TWITTER_REQUEST_TOKEN_URL)

            # Save the request token and secret in the session
            request.session["oauth_token"] = data["oauth_token"]
            request.session["oauth_token_secret"] = data["oauth_token_secret"]

            # Step 2: Redirect the user to Twitter's authorization page
            authorization_url = oauth.authorization_url(TWITTER_AUTHORIZE_URL)
            return redirect(authorization_url)

        except Exception as e:
            return JsonResponse(
                {"error": "Unable to initiate OAuth request."}, status=500
            )


class TwitterCallbackView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Step 3: Exchange the request token for an access token
        oauth_token = request.session.get("oauth_token")
        oauth_token_secret = request.session.get("oauth_token_secret")

        if not oauth_token or not oauth_token_secret:
            return JsonResponse({"error": "Missing OAuth token data."}, status=400)

        oauth = OAuth1Session(
            settings.TWITTER_API_KEY,
            client_secret=settings.TWITTER_API_SECRET_KEY,
            resource_owner_key=oauth_token,
            resource_owner_secret=oauth_token_secret,
            verifier=request.GET.get(
                "oauth_verifier"
            ),  # The verifier (PIN) from Twitter
        )

        try:
            # Fetch access tokens
            data = oauth.fetch_access_token(TWITTER_ACCESS_TOKEN_URL)

            # Extract access tokens
            access_token = data["oauth_token"]
            access_token_secret = data["oauth_token_secret"]
            user_id = data["user_id"]
            screen_name = data["screen_name"]

            # Save the access token to the user's social media account
            self.save_social_account(
                request.user, "twitter", access_token, access_token_secret
            )

            # Clear session data
            request.session.pop("oauth_token", None)
            request.session.pop("oauth_token_secret", None)

            return redirect("manage_accounts")

        except Exception as e:
            return JsonResponse({"error": "Unable to fetch access token."}, status=500)

    def save_social_account(self, user, platform, token, token_secret):
        # Save the social media account data to the user's account
        account, created = SocialMediaAccount.objects.get_or_create(user=user)

        if platform == "twitter":
            # Save both token and secret token for Twitter
            account.twitter = token  # Access Token
            account.twitter_secret = token_secret  # Secret Token

        account.save()


class CreatePostView(LoginRequiredMixin, View):
    template_name = "posts/create_post.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        title = request.POST.get("title")  # Get title from the form
        content = request.POST.get("content")
        image = request.FILES.get("image")
        share_to_twitter = request.POST.get("share_to_twitter") == "on"
        share_to_facebook = request.POST.get("share_to_facebook") == "on"
        share_to_instagram = request.POST.get("share_to_instagram") == "on"
        
        
        # Check if any of the social media options are selected
        if not (share_to_twitter or share_to_facebook or share_to_instagram):
            return JsonResponse({"error": "Please select at least one social media platform to share the post."}, status=400)


        if not title or not content:
            return JsonResponse(
                {"error": "Title and content cannot be empty."}, status=400
            )

        account = SocialMediaAccount.objects.filter(user=request.user).first()
        if not account:
            return JsonResponse(
                {"error": "Please link your social media accounts first."}, status=400
            )

        # Handle image saving to the filesystem (or cloud storage)
        if image:
            # Save image to storage (using default storage backend)
            image_path = default_storage.save("posts/images/" + image.name, image)
            image_url = default_storage.url(image_path)
        else:
            image_url = None

        post = Post.objects.create(
            user=request.user,
            title=title,  # Save the title
            content=content,
            image=image,
            shared_on_twitter=share_to_twitter and bool(account.twitter),
            shared_on_facebook=share_to_facebook and bool(account.facebook),
            shared_on_instagram=share_to_instagram and bool(account.instagram),
        )

        # Share on Twitter
        if share_to_twitter and account.twitter:
            twitter_data = {
                "title": post.title,
                "status": post.content,
                "media[]": image_url if image else None,
            }

            response = self.share_on_twitter(
                account.twitter, account.twitter_secret, twitter_data
            )
            if not response.get("success"):
                return JsonResponse(
                    {"error": "Failed to share on Twitter."}, status=500
                )

        # Share on Facebook
        if share_to_facebook and account.facebook:
            facebook_data = {
                "message": content,
                "access_token": account.facebook,
            }
            facebook_url = f"https://graph.facebook.com/me/feed"
            response = self.share_on_facebook(facebook_url, facebook_data)
            if not response.get("success"):
                return JsonResponse(
                    {"error": "Failed to share on Facebook."}, status=500
                )

        # Share on Instagram (using a third-party service for image posts)
        if share_to_instagram and account.instagram:
            instagram_data = {
                "image_url": image.url if image else None,
                "caption": content,
                "access_token": account.instagram,
            }
            instagram_url = "https://api.instagram.com/v1/media/upload"
            response = self.share_on_instagram(instagram_url, instagram_data)
            if not response.get("success"):
                return JsonResponse(
                    {"error": "Failed to share on Instagram."}, status=500
                )

        # If everything is successful, return a success response
        return JsonResponse({"success": True, "message": "Post created successfully!"})

    def share_on_twitter(self, access_token, secret_token, data):
        """
        Logic to share a post on Twitter using API v2.
        You need to handle OAuth1 session and post request for Twitter API v2.
        """
        # Initialize the Tweepy client (Twitter API v2)
        client = tweepy.Client(
            bearer_token=settings.TWITTER_API_KEY,
            access_token=access_token,
            access_token_secret=secret_token,
            consumer_key=settings.TWITTER_API_KEY,
            consumer_secret=settings.TWITTER_API_SECRET_KEY,
        )

        # Prepare the tweet text with title and content
        tweet_text = (
            f"Title: {data.get('title')}\n\n{data.get('status')}"  # Title + Content
        )

        try:

            # Check if there's an image to be uploaded
            media_id = None
            if "media[]" in data:
                media_path = data["media[]"]

                # Check if the file exists

                corrected_media_path = os.path.join(
                    settings.MEDIA_ROOT, media_path.lstrip("/")
                )
                corrected_media_path = corrected_media_path.replace(
                    "media/media/", "media/"
                )

                if not os.path.exists(corrected_media_path):
                    return {
                        "success": False,
                        "error": f"File not found: {corrected_media_path}",
                    }

                # Use Tweepy API v1.1 to upload the media
                auth = tweepy.OAuthHandler(
                    settings.TWITTER_API_KEY, settings.TWITTER_API_SECRET_KEY
                )
                auth.set_access_token(access_token, secret_token)
                api = tweepy.API(auth)

                # Upload media using Tweepy API v1.1
                media = api.media_upload(corrected_media_path)  # Pass file path
                media_id = media.media_id
        except Exception as e:
            media_id = None

        # Create the tweet with media (if media was uploaded)
        if media_id:
            tweet = client.create_tweet(text=tweet_text, media_ids=[media_id])
        else:
            tweet = client.create_tweet(text=tweet_text)

        # Check the response status
        if tweet:
            return {"success": True, "tweet_id": tweet}

        # Handle errors if the request fails
        return {"success": False, "error": "Failed to post the tweet"}

    def share_on_facebook(self, url, data):
        """
        Logic to share a post on Facebook.
        """
        response = requests.post(url, data=data)
        if response.status_code == 200:
            return {"success": True}
        return {"success": False, "error": response.json()}

    def share_on_instagram(self, url, data):
        """
        Logic to share a post on Instagram using the Instagram Graph API.
        This assumes the user has a Business Account linked to their Facebook.
        """
        instagram_account_id = (
            settings.INSTAGRAM_ACCOUNT_ID
        )  # Your Instagram Business Account ID
        access_token = data[
            "access_token"
        ]  # Long-lived Instagram Graph API access token

        # Step 1: Upload the image to Instagram
        image_url = data["image_url"]
        image_upload_url = (
            f"https://graph.facebook.com/v14.0/{instagram_account_id}/media"
        )
        image_data = {"image_url": image_url, "access_token": access_token}

        image_response = requests.post(image_upload_url, data=image_data)
        if image_response.status_code != 200:
            return {"success": False, "error": "Failed to upload image to Instagram."}

        image_media_id = image_response.json().get("id")

        # Step 2: Create the Instagram post
        create_post_url = (
            f"https://graph.facebook.com/v14.0/{instagram_account_id}/media_publish"
        )
        post_data = {"creation_id": image_media_id, "access_token": access_token}

        post_response = requests.post(create_post_url, data=post_data)
        if post_response.status_code == 200:
            return {"success": True}
        return {"success": False, "error": post_response.json()}


class ManageAccountsView(LoginRequiredMixin, View):
    template_name = "posts/manage_accounts.html"

    def get(self, request, *args, **kwargs):
        account = SocialMediaAccount.objects.filter(user=request.user).first()
        return render(request, self.template_name, {"account": account})

    def post(self, request, *args, **kwargs):
        # Retrieve current social media account or create one if it doesn't exist
        account, created = SocialMediaAccount.objects.get_or_create(user=request.user)

        # Get form data, preserving existing values if no new data is provided
        twitter = request.POST.get("twitter", "").strip()
        facebook = request.POST.get("facebook", "").strip()
        instagram = request.POST.get("instagram", "").strip()

        # Only update fields if new values are provided
        if twitter:
            account.twitter = twitter
        if facebook:
            account.facebook = facebook
        if instagram:
            account.instagram = instagram

        # Save updated account info
        try:
            account.save()
            return JsonResponse({"message": "Accounts updated successfully!"})
        except Exception as e:
            return JsonResponse(
                {"message": f"Error updating accounts: {str(e)}"}, status=500
            )
