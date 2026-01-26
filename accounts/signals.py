from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Account, UserProfile
from allauth.account.signals import user_signed_up, user_logged_in
from allauth.socialaccount.models import SocialAccount
from django.core.files.base import ContentFile
import requests

from .models import UserProfile, Account
# Import your cart models to handle the cart logic
from carts.models import Cart, CartItem 
from carts.views import _cart_id # Assuming _cart_id is importable, otherwise copy logic here

@receiver(user_signed_up)
def create_profile_from_social(request, user, **kwargs):
    """
    Runs only when a user registers via Social Login (Google/FB).
    Creates UserProfile and downloads the profile picture.
    """
    # 1. Create UserProfile if it doesn't exist
    profile, created = UserProfile.objects.get_or_create(user=user)

    # 2. Get Social Account Data
    if SocialAccount.objects.filter(user=user, provider='google').exists():
        social_acc = SocialAccount.objects.get(user=user, provider='google')
        data = social_acc.extra_data
        
        # Google specific data mapping
        picture_url = data.get('picture')
        
        # Download and save the image
        if picture_url:
            try:
                response = requests.get(picture_url)
                if response.status_code == 200:
                    profile.profile_picture.save(
                        f"google_profile_{user.id}.jpg", 
                        ContentFile(response.content), 
                        save=True
                    )
            except Exception as e:
                print(f"Error downloading image: {e}")
                profile.profile_picture = 'default/cat.png' # Fallback
                profile.save()
    
    # Save default if no social image found
    if not profile.profile_picture:
        profile.profile_picture = 'default/cat.png'
        profile.save()



# accounts/signals.py

# accounts/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Account, UserProfile

@receiver(post_save, sender=Account)
def post_save_create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            # Create the profile if it does not exist
            UserProfile.objects.create(user=instance)

@receiver(pre_save, sender=Account)
def pre_save_profile_receiver(sender, instance, **kwargs):
    pass
        
@receiver(user_logged_in)
def move_cart_to_user(request, user, **kwargs):
    """
    This signal runs whenever a user logs in (Manual OR Google).
    It replaces the cart merging logic inside your login view.
    """
    try:
        # Get the guest cart using session key
        session_cart_id = request.session.session_key 
        # OR use your _cart_id(request) logic here if possible
        if not session_cart_id:
            session_cart_id = request.session.create()

        cart = Cart.objects.get(cart_id=session_cart_id)
        is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
        
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(cart=cart)
            
            # ... [INSERT YOUR EXACT CART MERGING LOGIC HERE] ...
            # The logic you pasted in your view regarding product_variation, 
            # ex_var_list, and moving items to user.
            
            product_variation = []
            for item in cart_item:
                variation = item.variations.all()
                product_variation.append(list(variation))

            cart_item = CartItem.objects.filter(cart=cart) # Refresh queryset
            for item in cart_item:
                # Logic to check if user already has this item
                existing_cart_items = CartItem.objects.filter(user=user, product=item.product)
                
                if existing_cart_items.exists():
                     # ... (Your logic to match variations and increase quantity) ...
                     pass 
                else:
                    item.user = user
                    item.cart = None # Remove relation to guest cart
                    item.save()
            
            # Cleanup guest cart
            CartItem.objects.filter(cart=cart).delete()
    except Cart.DoesNotExist:
        pass