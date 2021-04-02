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
from .decorators import unauthenticated_user, allowed_users

from django.core.exceptions import ObjectDoesNotExist

from .models import *

from time import sleep
from datetime import datetime

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

    show_logout = False
    context = {
        'form': form,
        'show_logout': show_logout
    }
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

    show_logout = False
    context = {
        'form': form,
        'show_logout': show_logout
    }
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
            messages.error(request, 'Username or password is incorrect')     
            
    context = {'show_logout': False}
    return render(request, 'authentication/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def homePage(request):
    user_group = str(request.user.groups.all()[0])
    restaurants = Restaurant.objects.all()
    current_time = datetime.now().time()
    open_restaurants = [restaurant for restaurant in restaurants if ((restaurant.open_time < current_time and restaurant.close_time > current_time) or (restaurant.close_time < restaurant.open_time and restaurant.open_time < current_time))]
    closed_restaurants = [restaurant for restaurant in restaurants if not ((restaurant.open_time < current_time and restaurant.close_time > current_time) or (restaurant.close_time < restaurant.open_time and restaurant.open_time < current_time))]
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
        'open_restaurants': open_restaurants,
        'closed_restaurants': closed_restaurants,
        'user_group': user_group, 
        'users_restaurant': users_restaurant,
        'cart_counter': cart_counter
    }
    return render(request, 'authentication/index.html', context)

@login_required(login_url='login')
def restaurantPage(request, pk):
    user_group = str(request.user.groups.all()[0])
    restaurant = Restaurant.objects.get(id = pk)
    available_foods = Food.objects.filter(restaurant = restaurant)
    current_time = datetime.now().time()
    if (restaurant.owner_id == str(request.user.id)):
        is_owner = True
        is_closed = False
    else:
        is_owner = False
        if (restaurant.open_time < current_time and restaurant.close_time > current_time) or (restaurant.close_time < restaurant.open_time and restaurant.open_time < current_time):
            is_closed = False
        else:
            is_closed = True
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
        'cart_counter': cart_counter,
        'is_closed': is_closed
    }
    return render(request, 'restaurants/restaurant.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles = ['restaurant'])
def restaurantDetailPage(request, pk):
    if (int(request.user.id) != int(pk)):
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
@allowed_users(allowed_roles = ['restaurant'])
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
@allowed_users(allowed_roles = ['restaurant'])
def modifyFoodPage(request, pk):
    food = Food.objects.get(id = pk)
    if (int(request.user.id) != int(food.restaurant.owner_id)):
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
@allowed_users(allowed_roles = ['restaurant'])
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
        for cart in Cart.objects.filter(food = food):
            cart.delete()
        food.delete()
        return redirect('restaurant', users_restaurant.id)

    context = {
        'item': food, 
        'users_restaurant': users_restaurant
    }
    return render(request, 'foods/delete_food.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles = ['customer'])
def foodToCart(request, pk):
    user_id = request.user.id
    current_time = datetime.now().time()
    try:
        food = Food.objects.get(id = pk)
        foods_restaurant = food.restaurant
        if not (foods_restaurant.open_time < current_time and foods_restaurant.close_time > current_time) or (foods_restaurant.close_time < foods_restaurant.open_time and foods_restaurant.open_time < current_time):
            return redirect('/')
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
@allowed_users(allowed_roles = ['customer'])
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

        email_subject = 'A new order has been recieved'
        my_dict = {}
        for element in cart_elements:
            if element.food.restaurant.name not in my_dict.keys():
                my_dict[element.food.restaurant.name] = []
                my_dict[element.food.restaurant.name].append({
                    'food_name': element.food.name,
                    'amount': element.amount,
                    'sum_price': element.sum_price
                })
            else:
                my_dict[element.food.restaurant.name].append({
                    'food_name': element.food.name,
                    'amount': element.amount,
                    'sum_price': element.sum_price
                })
        for restaurant in my_dict:
            orders_total_price = 0
            email_body = 'We recieved an order for the foods below:\n'
            for food in my_dict[restaurant]:
                email_body += '    - ' + food['food_name'] + ' (' + food['amount'] + ' piece) ($' + food['sum_price'] + ')\n'
                orders_total_price += float(food['sum_price'])
            email_body += '\nOrder details:\n'
            email_body += '    - Name: ' + fs.customer_name + '\n    - Customer\'s phone number: ' + fs.phone_number + '\n    - Delivery address: ' + fs.address
            if fs.description != None:
                email_body += '\n    - Description: ' + fs.description
            email_body += '\nTotal price: $' + str(round(orders_total_price, 2))
            email_body += '\n\nRegards,\nFoodStation Team'

            restaurant = Restaurant.objects.get(name = restaurant)
            user = User.objects.get(id = restaurant.owner_id)
            email = user.email
            email = EmailMessage(
                email_subject,
                email_body,
                'noreply@foodstation.com',
                [email]
            )
            email.send(fail_silently=False)
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
@allowed_users(allowed_roles = ['customer'])
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
@allowed_users(allowed_roles = ['customer'])
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
@allowed_users(allowed_roles = ['customer'])
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
        'customer_name': orders[0].customer_name,
        'phone_number': orders[0].phone_number,
        'address': orders[0].address,
        'description': orders[0].description,
        "cart_counter": cart_counter
    }
    return render(request, 'order/order.html', context)