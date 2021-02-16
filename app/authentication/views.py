from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

from .forms import *
from .decorators import unauthenticated_user, allowed_users, admin_only

from django.core.exceptions import ObjectDoesNotExist

from .models import *

# Create your views here.

@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            group = Group.objects.get(name = 'customer')
            user.groups.add(group)

            messages.success(request, 'Account was created for ' + username)

            return redirect('login')

    context = {'form': form}
    return render(request, 'authentication/register.html', context)

@unauthenticated_user
def registerRestaurantPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            group = Group.objects.get(name = 'restaurant')
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

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def homePage(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'authentication/index.html', {'restaurants' : restaurants})

@login_required(login_url='login')
@admin_only
def adminPage(request):
    return render(request, 'accounts/admin.html')

@login_required(login_url='login')
@allowed_users(allower_roles = ['customer'])
def userPage(request):
    context = {}
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

    context = {'restaurant': restaurant, 'available_foods': available_foods, 'is_owner': is_owner, 'user_group': user_group}
    return render(request, 'restaurants/restaurant.html', context)

@login_required(login_url='login')
@allowed_users(allower_roles = ['restaurant'])
def deleteRestaurant(request, pk):
    restaurant = Restaurant.objects.get(id = pk)

    if request.method == "POST":
        restaurant.delete()
        return redirect('/')

    context = {'item': restaurant}
    return render(request, 'restaurants/delete_restaurant.html', context)

@login_required(login_url='login')
@allowed_users(allower_roles = ['restaurant'])
def restaurantDetailPage(request, pk):
    if (int(request.user.id) != int(pk)): 
        print('Incorrect id')
        return redirect('/')

    try:
        restaurant = Restaurant.objects.get(owner_id = pk)
        form = RestaurantForm(instance = restaurant)

        if request.method == "POST":
            form = RestaurantForm(request.POST, instance = restaurant)
            if form.is_valid():
                fs = form.save(commit = False)
                fs.owner_id = str(request.user.id)
                fs.save()
                return redirect('/')
        context = {'form': form, 'restaurant': restaurant}
        return render(request, 'restaurants/restaurant_detail.html', context)
    except ObjectDoesNotExist:
        print('doesnt exist')
        form = RestaurantForm()

        if request.method == "POST":
            form = RestaurantForm(request.POST)
            if form.is_valid():
                fs = form.save(commit = False)
                fs.owner_id = str(request.user.id)
                fs.save()
                return redirect('/')
        context = {'form': form}
        return render(request, 'restaurants/restaurant_form.html', context)

    return render(request, 'restaurants/restaurant_detail.html')

@login_required(login_url='login')
@allowed_users(allower_roles = ['restaurant'])
def addFoodPage(request, pk):
    restaurant = Restaurant.objects.get(id = pk)
    if (int(request.user.id) != int(restaurant.owner_id)): 
        return redirect('/')

    form = FoodForm()

    if request.method == 'POST':
        form = FoodForm(request.POST)
        if form.is_valid():
            fs = form.save(commit = False)
            fs.restaurant = restaurant
            fs.save()
            return redirect('/')

    context = {'form': form}
    return render(request, 'foods/add_food_form.html', context)

@login_required(login_url='login')
@allowed_users(allower_roles = ['restaurant'])
def modifyFoodPage(request, pk):
    food = Food.objects.get(id = pk)
    if (int(request.user.id) != int(food.restaurant.owner_id)): 
        print('Incorrect id')
        return redirect('/')

    form = FoodForm(instance = food)

    if request.method == "POST":
        form = FoodForm(request.POST, instance = food)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form': form}
    return render(request, 'foods/modify_food_form.html', context)

@login_required(login_url='login')
@allowed_users(allower_roles = ['restaurant'])
def deleteFood(request, pk):
    food = Food.objects.get(id = pk)
    if (int(request.user.id) != int(food.restaurant.owner_id)): 
        print('Incorrect id')
        return redirect('/')

    if request.method == "POST":
        food.delete()
        return redirect('/')

    context = {'item': food}
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
        price = int(cart.sum_price) + int(food.price)
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

    return redirect('/')

@login_required(login_url='login')
@allowed_users(allower_roles = ['customer'])
def cartPage(request):
    user_id = request.user.id
    cart_elements = Cart.objects.filter(user_id = user_id)
    total_price = sum([int(element.sum_price) for element in cart_elements])
    if total_price:
        is_empty = False
    else:
        is_empty = True
    context = {'cart_elements': cart_elements, 'total_price': total_price, 'is_empty': is_empty}
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
        cart.sum_price = int(cart.sum_price) + int(cart.food.price)
        cart.save()
    elif action == 'dcr':
        if int(cart.amount) > 1:
            cart.amount = int(cart.amount) - 1
            cart.sum_price = int(cart.sum_price) - int(cart.food.price)
            cart.save()
    elif action == 'del':
        cart.delete()

    return redirect('cart')

@login_required(login_url='login')
@allowed_users(allower_roles = ['customer'])
def placeOrder(request):
    cart_elements = Cart.objects.filter(user_id = request.user.id)
    users_orders = Order.objects.filter(user_id = request.user.id)
    
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

@login_required(login_url='login')
@allowed_users(allower_roles = ['customer'])
def orderPlacedPage(request):
    orders = Order.objects.filter(user_id = request.user.id)
    orders_set = []
    order_counters = []
    for order in orders:
        if order.order_counter not in order_counters:
            orders_set.append(order)
            order_counters.append(order.order_counter)
    context = {'orders_set': orders_set}
    return render(request, 'order/order_placed.html', context)

@login_required(login_url='login')
@allowed_users(allower_roles = ['customer'])
def orderPage(request, pk):
    orders = Order.objects.filter(order_counter = pk)
    date = orders[0].order_date
    total_price = sum([int(element.sum_price) for element in orders])

    context = {'orders': orders, 'date': date, 'total_price': total_price}
    return render(request, 'order/order.html', context)