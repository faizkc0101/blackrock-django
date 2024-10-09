from django.shortcuts import render, redirect, HttpResponse
from .forms import RegisterForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.conf import settings

from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
import random

def register(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            user = Account.objects.create_user(
                first_name=first_name, 
                last_name=last_name, 
                email=email, 
                username=username, 
                password=password
            )
            user.phone_number = phone_number
            user.is_active = False  # for test false in models.py
            user.save() 

            otp = random.randint(1000, 9999)
            request.session['otp'] = otp
            request.session['email'] = email 

            send_mail(
                'Verify your email',
                f'Your OTP for verification is {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False  
            )

            messages.success(request, "OTP has been sent to your email for verification")
            return render(request, 'accounts/verify.html')
        else:
            messages.error(request, "Something went wrong.")
    
    context = {'form': form}
    return render(request, 'accounts/register.html', context)

def verify(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp') 
        stored_otp = request.session.get('otp')  
        stored_email = request.session.get('email')

        if str(stored_otp) == entered_otp:
            user = Account.objects.get(email=stored_email)
            user.is_active = True 
            user.save()

            del request.session['otp']
            del request.session['email']

            messages.success(request, "OTP verified successfully! You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'accounts/verify.html')

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(username=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are logged in')
            return redirect('home')
        else:
            messages.error(request, 'Invalid login credentials')

    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out')
    return redirect('login')

def generate_reset_token(user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    return uid,token

def forgetpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = Account.objects.get(email=email)
            uid, token = generate_reset_token(user)

            reset_link = f'http://127.0.0.1:8000/accounts/reset/{uid}/{token}/'
            send_mail(
                'Reset Your Password',
                f'Hello {user.first_name},\n\nTo reset your password, click the link below:\n{reset_link}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False  
            )
            messages.success(request, 'A password reset link has been sent to your email.')
            return redirect('login')
        except Account.DoesNotExist:
            messages.error(request, 'No account found with this email.')

    return render(request, 'accounts/forgetpassword.html')

def newpassword(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Account.objects.get(pk=uid)

        if not default_token_generator.check_token(user, token):
            return HttpResponse('The password reset link is invalid or has expired.')

        if request.method == 'POST':
            pass1 = request.POST.get('password1')
            pass2 = request.POST.get('password2')

            if pass1 and pass2:
                if pass1 == pass2:
                    user.set_password(pass1)
                    user.save()
                    messages.success(request, 'Your password has been reset successfully.')
                    return redirect('login')
                else:
                    messages.error(request, 'Passwords do not match.')

            messages.error(request, 'Please enter both passwords.')

        return render(request, 'accounts/newpassword.html', {'username': user.username})

    except Account.DoesNotExist:
        return HttpResponse('User not found.')
