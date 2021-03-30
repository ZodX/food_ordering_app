from django.contrib import admin
from django.urls import path

from authentication.views import *

urlpatterns = [
    path('', loginPage),
    path('admin/', admin.site.urls),
    path('login/', loginPage, name='login'),
    path('register/', registerPage, name='register'),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name = 'activate'),
    path('registerRestaurant/', registerRestaurantPage, name='registerRestaurant'),
    path('home/', homePage, name='home'),
    path('logout/', logoutUser, name='logout'),
    path('restaurant/<str:pk>/', restaurantPage, name='restaurant'),
    path('restaurant_detail/<str:pk>', restaurantDetailPage, name='restaurant_detail'),
    path('add_food/<str:pk>', addFoodPage, name='add_food_form'),
    path('modify_food/<str:pk>', modifyFoodPage, name='modify_food_form'),
    path('delete_food/<str:pk>', deleteFood, name='delete_food'),
    path('food_to_cart/<str:pk>', foodToCart, name='food_to_cart'),
    path('cart/', cartPage, name='cart'),
    path('manage_cart/<str:pk>', manageCart, name='manage_cart'),
    path('order_placed/', orderPlacedPage, name='order_placed'),
    path('order/<str:pk>', orderPage, name='order')
]
