from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from orders.models import Order, OrderProduct

# Verification Email
from django.contrib.sites.shortcuts import get_current_site as get_current_site
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from carts.models import Cart, CartItem
from carts.views import merge_cart
import requests

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()
            

            # Update the user profile created by signals
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.profile_picture = 'default/cat.png'
            profile.save()

            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(
                mail_subject,
                message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[to_email]
            )
            email_sent = False
            try:
                if getattr(settings, 'EMAIL_HOST_PASSWORD', None):
                    send_email.send()
                    email_sent = True
            except Exception as e:
                print(f"Error sending activation email: {e}")

            if email_sent:
                return redirect('/accounts/login/?command=verification&email=' + email)
            else:
                messages.success(request, 'Registration successful! Your account is active and you can now log in directly.')
                return redirect('accounts:login')
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)



def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            merge_cart(request, user)
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            
            # Check for 'next' redirect parameter
            next_url = request.GET.get('next') or request.POST.get('next')
            if not next_url:
                referer = request.META.get('HTTP_REFERER')
                if referer and 'next=' in referer:
                    try:
                        query = requests.utils.urlparse(referer).query
                        for part in query.split('&'):
                            if part.startswith('next='):
                                next_url = part.split('=', 1)[1]
                                break
                    except Exception:
                        pass
            
            if next_url:
                return redirect(next_url)
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('accounts:login')
    return render(request, 'accounts/login.html')


@login_required(login_url='accounts:login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('accounts:login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('accounts:login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('accounts:register')
    
@login_required(login_url='accounts:login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()
    # orders = (
    #     .exclude(order_id__isnull=True)
    #     .exclude(order_id__exact='')
    # )
    context = {
        'orders': orders,
        'orders_count': orders_count,
        
    }
    return render(request, 'accounts/dashboard.html', context)


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email):
            user = Account.objects.get(email__exact=email)
            
            # Reset Password Email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(
                mail_subject,
                message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[to_email]
            )
            email_sent = False
            try:
                if getattr(settings, 'EMAIL_HOST_PASSWORD', None):
                    send_email.send()
                    email_sent = True
            except Exception as e:
                print(f"Error sending password reset email: {e}")
            
            if email_sent:
                messages.success(request, 'Password reset email has been sent to your email address.')
            else:
                messages.warning(request, 'Email service is currently offline. Please contact admin to reset your password.')
            return redirect('accounts:login')  
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('accounts:forgotPassword')
    return render(request, 'accounts/forgotPassword.html')

def resetPassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('accounts:resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('accounts:login')
    
    
def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful. You can login now.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('accounts:resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')
    


# def change_password(request):
#     if request.method == 'POST':
#         current_password = request.POST['current_password']
#         new_password = request.POST['new_password']
#         confirm_password = request.POST['confirm_password']
        
#         user = Account.objects.get(username__exact=request.user.username)
        
#         if new_password == confirm_password:
#             success = user.check_password(current_password)
#             if success:
#                 user.set_password(new_password)
#                 user.save()
#                 messages.success(request, 'Password updated successfully.')
#                 return redirect('change_password')
#             else:
#                 messages.error(request, 'Please enter valid current password')
#                 return redirect('change_password')
#         else:
#             messages.error(request, 'Password does not match!')
#             return redirect('change_password')
#     return render(request, 'accounts/login.html')

@login_required(login_url='accounts:login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)

@login_required(login_url='accounts:login')
def edit_profile(request):
    try:
        userprofile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        userprofile = UserProfile.objects.create(user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('accounts:edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)
@login_required(login_url='accounts:login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        
        user = Account.objects.get(username__exact=request.user.username)
        
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password updated successfully.')
                return redirect('accounts:change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('accounts:change_password')
    return render(request, 'accounts/change_password.html')

@login_required(login_url='accounts:login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    # calculate subtotal from order items
    subtotal = 0
    items_with_totals = []
    for item in order_detail:
        try:
            line_total = item.product_price * item.quantity
        except Exception:
            line_total = item.product.price * item.quantity
        subtotal += line_total
        items_with_totals.append({
            'item': item,
            'line_total': line_total,
        })
    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
        'items_with_totals': items_with_totals,
    }
    return render(request, 'accounts/order_detail.html', context)

def helps(request):
    return render(request, 'accounts/help.html')