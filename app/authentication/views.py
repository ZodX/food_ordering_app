from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.core.mail import EmailMessage
from django.views import View
from django.urls import reverse

from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site

from utils import token_generator

from .forms import *
from .decorators import unauthenticated_user, allowed_users, admin_only

from django.core.exceptions import ObjectDoesNotExist

from .models import *

from time import sleep

class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk = id)

            if not token_generator.check_token(user, token):
                return redirect('login' + '?message=' + 'User already activated')

            if user.is_active:
                return redirect('login')
            
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully')
            return redirect('login')
        except Exception as ex:
            print("EXCEPTION OCCURED")
            print(ex)
            pass

        return redirect('login')

@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password1']
            
            check_user = User.objects.filter(email=email)
            if len(check_user) > 0:
                messages.error(request, 'User with email already exists')
                sleep(1)
                return redirect('register')

            user = User.objects.create_user(username = username, email = email)
            user.set_password(password)
            user.is_active = False
            user.save()
            group = Group.objects.get(name = 'customer')
            user.groups.add(group)

            email_subject = 'Activate your account'

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            link = reverse('activate', kwargs = {'uidb64': uidb64, 'token': token_generator.make_token(user)})
            activate_url = 'http://' + domain + link

            email_body = 'Hi ' + user.username + '!\n\n' + 'Please use this link to verify your account:\n' + activate_url + '\n\nRegards,\nFoodStation team'
            email = EmailMessage(
                email_subject,
                email_body,
                'noreply@foodstation.com',
                [email]
            )
            email.send(fail_silently=False)
            messages.warning(request, 'Please verify your email...')
            return redirect('login')

    context = {'form': form}
    return render(request, 'authentication/register.html', context)

@unauthenticated_user
def registerRestaurantPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password1']

            check_user = User.objects.filter(email=email)
            if len(check_user) > 0:
                messages.error(request, 'User with email already exists')
                sleep(1)
                return redirect('register')

            user = User.objects.create_user(username = username, email = email)
            user.set_password(password)
            user.is_active = False
            user.save()
            group = Group.objects.get(name = 'restaurant')
            user.groups.add(group)

            email_subject = 'Activate your account'

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            link = reverse('activate', kwargs = {'uidb64': uidb64, 'token': token_generator.make_token(user)})
            activate_url = 'http://' + domain + link

            email_body = 'Hi ' + user.username + '!\n\n' + 'Please use this link to verify your account:\n' + activate_url + '\n\nRegards,\nFoodStation team'
            email = EmailMessage(
                email_subject,
                email_body,
                'noreply@foodstation.com',
                [email]
            )
            email.send(fail_silently=False)
            messages.warning(request, 'Please verify your email...')
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
            
    context = {'show_logout': False}
    return render(request, 'authentication/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def homePage(request):
    user_group = str(request.user.groups.all()[0])
    restaurants = Restaurant.objects.all()
    if user_group == 'restaurant':
        try:
            users_restaurant = Restaurant.objects.get(owner_id = request.user.id)
        except ObjectDoesNotExist:
            users_restaurant = None
    else:
        users_restaurant = None

    cart_counter = sum([int(element.amount) for element in Cart.objects.filter(user_id = request.user.id)])

    context = {
        'restaurants': restaurants, 
        'user_group': user_group, 
        'users_restaurant': users_restaurant,
        'cart_counter': cart_counter
    }
    return render(request, 'authentication/index.html', context)

@login_required(login_url='login')
@admin_only
def adminPage(request):
    return render(request, 'accounts/admin.html')

@login_required(login_url='login')
def userPage(request):
    user_group = str(request.user.groups.all()[0])
    context = {'user_group': user_group}
    return render(request, 'accounts/user.html', context)

@login_required(login_url='login')
def restaurantPage(request, pk):
    user_group = str(request.user.groups.all()[0])
    restaurant = Restaurant.objects.get(id = pk)
    available_foods = Food.objects.filter(restaurant = restaurant)
    if (restaurant.owner_id == str(request.user.id)):
        is_owner = True
    else:
        is_owner = False
    if user_group == 'restaurant':
        try:
            users_restaurant = Restaurant.objects.get(owner_id = request.user.id)
        except ObjectDoesNotExist:
            users_restaurant = None
    else:
        users_restaurant = None
    food_count = len(available_foods)
    cart_counter = sum([int(element.amount) for element in Cart.objects.filter(user_id = request.user.id)])
    context = {
        'restaurant': restaurant,
        'available_foods': available_foods,
        'is_owner': is_owner,
        'user_group': user_group,
        'users_restaurant': users_restaurant,
        'food_count': food_count,
        'cart_counter': cart_counter
    }
    return render(request, 'restaurants/restaurant.html', context)

@login_required(login_url='login')
@allowed_users(allower_roles = ['restaurant'])
def restaurantDetailPage(request, pk):
    if (int(request.user.id) != int(pk)): 
        print('Incorrect id')
        return redirect('/')

    user_group = str(request.user.groups.all()[0])
    if user_group == 'restaurant':
        try:
            users_restaurant = Restaurant.objects.get(owner_id = request.user.id)
        except ObjectDoesNotExist:
            users_restaurant = None

    try:
        restaurant = Restaurant.objects.get(owner_id = pk)
        form = RestaurantForm(instance = restaurant)

        if request.method == "POST":
            form = RestaurantForm(request.POST, instance = restaurant)
            if form.is_valid():
                fs = form.save(commit = False)
                fs.owner_id = str(request.user.id)
                fs.save()
                return redirect('restaurant', restaurant.id)
        context = {
            'form': form, 
            'restaurant': restaurant,
            'users_restaurant': users_restaurant
        }
    except ObjectDoesNotExist:
        print('doesnt exist')
        form = RestaurantForm()

        if request.method == "POST":
            form = RestaurantForm(request.POST)
            if form.is_valid():
                fs = form.save(commit = False)
                fs.owner_id = str(request.user.id)
                fs.save()
                restaurant = Restaurant.objects.get(owner_id = pk)
                return redirect('restaurant', restaurant.id)
        context = {
            'form': form,
            'users_restaurant': users_restaurant
        }

    return render(request, 'restaurants/restaurant_detail.html', context)

@login_required(login_url='login')
@allowed_users(allower_roles = ['restaurant'])
def addFoodPage(request, pk):
    restaurant = Restaurant.objects.get(id = pk)
    if (int(request.user.id) != int(restaurant.owner_id)): 
        return redirect('/')

    user_group = str(request.user.groups.all()[0])
    if user_group == 'restaurant':
        try:
            users_restaurant = Restaurant.objects.get(owner_id = request.user.id)
        except ObjectDoesNotExist:
            users_restaurant = None

    form = FoodForm()

    print(users_restaurant)
    if request.method == 'POST':
        form = FoodForm(request.POST)
        if form.is_valid():
            fs = form.save(commit = False)
            try:
                float(fs.price)
                fs.restaurant = restaurant
                fs.save()
                return redirect('restaurant', restaurant.id)
            except: 
                pass
    context = {
        'form': form,
        'user_group': user_group,
        'users_restaurant': users_restaurant
    }
    return render(request, 'foods/add_food_form.html', context)

@login_required(login_url='login')
@allowed_users(allower_roles = ['restaurant'])
def modifyFoodPage(request, pk):
    food = Food.objects.get(id = pk)
    if (int(request.user.id) != int(food.restaurant.owner_id)): 
        print('Incorrect id')
        return redirect('/')

    user_group = str(request.user.groups.all()[0])
    if user_group == 'restaurant':
        try:
            users_restaurant = Restaurant.objects.get(owner_id = request.user.id)
        except ObjectDoesNotExist:
            users_restaurant = None

    form = FoodForm(instance = food)

    if request.method == "POST":
        form = FoodForm(request.POST, instance = food)
        if form.is_valid():
            try:
                fs = form.save(commit = False)
                print('he', fs.price)
                float(fs.price)
                form.save()
                return redirect('restaurant', users_restaurant.id)
            except: 
                pass

    context = {
        'form': form,
        'user_group': user_group,
        'users_restaurant': users_restaurant
    }
    return render(request, 'foods/modify_food_form.html', context)

@login_required(login_url='login')
@allowed_users(allower_roles = ['restaurant'])
def deleteFood(request, pk):
    food = Food.objects.get(id = pk)
    if (int(request.user.id) != int(food.restaurant.owner_id)): 
        print('Incorrect id')
        return redirect('/')

    user_group = str(request.user.groups.all()[0])
    if user_group == 'restaurant':
        try:
            users_restaurant = Restaurant.objects.get(owner_id = request.user.id)
        except ObjectDoesNotExist:
            users_restaurant = None

    if request.method == "POST":
        food.delete()
        return redirect('restaurant', users_restaurant.id)

    context = {
        'item': food, 
        'users_restaurant': users_restaurant
    }
    return render(request, 'foods/delete_food.html', context)

@login_required(login_url='login')
@allowed_users(allower_roles = ['customer'])
def foodToCart(request, pk):
    user_id = request.user.id
    try:
        food = Food.objects.get(id = pk)
    except ObjectDoesNotExist:
        print("Food DoesNotExist")
        return redirect('/')

    carts = Cart.objects.filter(user_id = user_id)
    found = False
    for temp_cart in carts:
        if temp_cart.food.id == int(pk):
            cart = temp_cart
            found = True
            break

    if found:
        amount = int(cart.amount) + 1
        price = float(cart.sum_price) + float(food.price)
        if price - round(price, 0) == 0:
            price = int(price)
        form = CartForm(request.POST, instance = cart)
        fs = form.save(commit = False)
        fs.food = food
        fs.user_id = user_id
        fs.amount = amount
        fs.sum_price = price
        fs.save()
    else:
        print("Cart DoesNotExist")
        form = CartForm(request.POST)
        fs = form.save(commit = False)
        fs.food = food
        fs.user_id = user_id
        fs.amount = 1
        fs.sum_price = food.price
        fs.save()

    return redirect('restaurant', food.restaurant.id)

@login_required(login_url='login')
@allowed_users(allower_roles = ['customer'])
def cartPage(request):
    user_id = request.user.id
    user_group = str(request.user.groups.all()[0])
    cart_elements = Cart.objects.filter(user_id = user_id)
    users_orders = Order.objects.filter(user_id = user_id)
    total_price = round(sum([float(element.sum_price) for element in cart_elements]), 2)

    if total_price - round(total_price, 0) == 0:
        total_price = int(total_price)

    form = OrderForm()

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if len(users_orders) > 0:
            users_order_counter = max([int(order.order_counter) for order in users_orders])
        else:
            users_order_counter = 0

        for element in cart_elements:
            form = OrderForm(request.POST)
            fs = form.save(commit = False)
            fs.order_counter = users_order_counter + 1
            fs.user_id = request.user.id
            fs.food = element.food
            fs.amount = element.amount
            fs.sum_price = element.sum_price
            fs.save()
            element.delete()
        return redirect('order_placed')
    
    cart_counter = sum([int(element.amount) for element in Cart.objects.filter(user_id = request.user.id)])
    context = {
        'cart_elements': cart_elements, 
        'total_price': total_price,
        'user_group': user_group,
        'cart_counter': cart_counter,
        'form': form
    }
    return render(request, 'cart/cart.html', context)

@login_required(login_url='login')
@allowed_users(allower_roles = ['customer'])
def manageCart(request, pk):
    cart = Cart.objects.get(id = pk)
    if (int(request.user.id) != int(cart.user_id)): 
        print('Incorrect id')
        return redirect('/')

    action = request.GET.get("action")
    if action == 'inc':
        cart.amount = int(cart.amount) + 1
        cart.sum_price = round(float(cart.sum_price) + float(cart.food.price), 2)
        if cart.sum_price - round(cart.sum_price, 0) == 0:
            cart.sum_price = int(cart.sum_price)
        cart.save()
    elif action == 'dcr':
        if int(cart.amount) > 1:
            cart.amount = int(cart.amount) - 1
            cart.sum_price = round(float(cart.sum_price) - float(cart.food.price), 2)
            if cart.sum_price - round(cart.sum_price, 0) == 0:
                cart.sum_price = int(cart.sum_price)
            cart.save()
    elif action == 'del':
        cart.delete()

    return redirect('cart')

@login_required(login_url='login')
@allowed_users(allower_roles = ['customer'])
def orderPlacedPage(request):
    user_group = str(request.user.groups.all()[0])
    orders = Order.objects.filter(user_id = request.user.id)
    orders_set = []
    order_counters = []
    for order in orders:
        if order.order_counter not in order_counters:
            current_counter = order.order_counter
            total_price = sum([float(o.sum_price) for o in orders if o.order_counter == current_counter])
            if total_price - round(total_price, 0) == 0:
                total_price = int(total_price)
            orders_set.append({
                'date': order.order_date,
                'address': order.address,
                'total_price': total_price,
                'order_counter': order.order_counter
            })
            order_counters.append(order.order_counter)

    cart_counter = sum([int(element.amount) for element in Cart.objects.filter(user_id = request.user.id)])
    order_counter = len(orders)
    context = {
        'orders_set': orders_set, 
        'user_group': user_group,
        'cart_counter': cart_counter,
        'order_counter': order_counter
    }
    return render(request, 'order/order_placed.html', context)

@login_required(login_url='login')
@allowed_users(allower_roles = ['customer'])
def orderPage(request, pk):
    users_orders = Order.objects.filter(user_id = request.user.id)
    if len(users_orders) > 0:
        users_order_counter = max([int(order.order_counter) for order in users_orders])
    else:
        users_order_counter = 0

    if int(users_order_counter) < int(pk):
        return redirect('/')

    user_group = str(request.user.groups.all()[0])
    order_records = Order.objects.filter(user_id = request.user.id)
    orders = [record for record in order_records if record.order_counter == pk]
    for order in orders:
        order.sum_price = round(float(order.sum_price), 2)
        if order.sum_price - round(order.sum_price, 0) == 0:
            order.sum_price = int(order.sum_price)
    date = orders[0].order_date
    total_price = sum([float(element.sum_price) for element in orders])
    if total_price - round(total_price, 0) == 0:
        total_price = int(total_price)
    cart_counter = sum([int(element.amount) for element in Cart.objects.filter(user_id = request.user.id)])

    context = {
        'orders': orders, 
        'date': date, 
        'total_price': total_price,
        'user_group': user_group,
        'phone_number': orders[0].phone_number,
        'address': orders[0].address,
        "cart_counter": cart_counter
    }
    return render(request, 'order/order.html', context)