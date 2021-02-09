"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from authentication.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', loginPage, name="login"),
    path('register/', registerPage, name="register"),
    path('registerRestaurant/', registerRestaurantPage, name='registerRestaurant'),
    path('home/', homePage, name="home"),
    path('logout/', logoutUser, name="logout"),
    path('user/', userPage, name='user'),
    path('adminPage/', adminPage, name='admin'),
    path('restaurant/<str:pk>/', restaurantPage, name='restaurant'),
    path('delete_restaurant/<str:pk>/', deleteRestaurant, name='delete_restaurant'),
    path('restaurant_detail/<str:pk>', restaurantDetailPage, name='restaurant_detail'),
    path('add_food/<str:pk>', addFoodPage, name='add_food_form'),
    path('modify_food/<str:pk>', modifyFoodPage, name='modify_food_form'),
    path('delete_food/<str:pk>', deleteFood, name='delete_food'),
    path('', loginPage)
]
