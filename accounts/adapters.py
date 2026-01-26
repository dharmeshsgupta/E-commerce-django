# accounts/adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        
        # If username is missing, generate it from email
        if not user.username and user.email:
            user.username = user.email.split('@')[0]
            
        # Fix for phone_number cannot be null
        if not user.phone_number:
            user.phone_number = ""
            
        return user