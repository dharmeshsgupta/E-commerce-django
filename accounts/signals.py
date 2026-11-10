from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.core.files.base import ContentFile
import requests

from .models import Account, UserProfile
from allauth.account.signals import user_signed_up
from allauth.socialaccount.models import SocialAccount
from carts.models import Cart, CartItem 
from carts.views import merge_cart

@receiver(user_signed_up)
def create_profile_from_social(request, user, **kwargs):
    """
    Runs only when a user registers via Social Login (Google/FB).
    Creates UserProfile and downloads the profile picture.
    """
    profile, created = UserProfile.objects.get_or_create(user=user)

    if SocialAccount.objects.filter(user=user, provider='google').exists():
        social_acc = SocialAccount.objects.get(user=user, provider='google')
        data = social_acc.extra_data
        
        picture_url = data.get('picture')
        
        if picture_url:
            try:
                response = requests.get(picture_url, timeout=5)
                if response.status_code == 200:
                    profile.profile_picture.save(
                        f"google_profile_{user.id}.jpg", 
                        ContentFile(response.content), 
                        save=True
                    )
            except Exception as e:
                print(f"Error downloading image: {e}")
                profile.profile_picture = 'default/cat.png'
                profile.save()
    
    if not profile.profile_picture:
        profile.profile_picture = 'default/cat.png'
        profile.save()

@receiver(post_save, sender=Account)
def post_save_create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=instance)

@receiver(pre_save, sender=Account)
def pre_save_profile_receiver(sender, instance, **kwargs):
    pass
        
@receiver(user_logged_in)
def move_cart_to_user(sender, request, user, **kwargs):
    """
    This signal runs whenever a user logs in (Manual OR Social).
    Merges guest cart items with existing user cart items.
    """
    merge_cart(request, user)
