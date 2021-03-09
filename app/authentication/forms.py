from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from .models import *

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class RestaurantForm(ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'address']

class FoodForm(ModelForm):
    class Meta:
        model = Food
        fields = ['name', 'price', 'description']

class CartForm(ModelForm):
    class Meta:
        model = Cart
        fields = []

class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'phone_number', 'address', 'description']