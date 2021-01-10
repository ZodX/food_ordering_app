from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

from .forms import CreateUserForm
from .decorators import unauthenticated_user, allowed_users, admin_only

# Create your views here.

@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            group = Group.ogjects.get(name = 'customer')
            user.groups.add(group)

            messages.success(request, 'Account was created for ' + username)

            return redirect('login')

    context = {'form': form}
    return render(request, 'authentication/register.html', context)

@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or password is incorrect')     
            
    context = {}
    return render(request, 'authentication/login.html', context)

@login_required(login_url='login')
def homePage(request):
    return render(request, 'authentication/index.html')

@login_required(login_url='login')
@admin_only
def adminPage(request):
    return render(request, 'accounts/admin.html')

@login_required(login_url='login')
@allowed_users(allower_roles = ['customer'])
def userPage(request):
    context = {}
    return render(request, 'accounts/user.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')