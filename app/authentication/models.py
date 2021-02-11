from django.db import models


# Create your models here

""" class Customer(models.Model):
    name = models.CharField(max_length = 200, null = True)
    phone = models.CharField(max_length = 200, null = True)
    email = models.CharField(max_length = 200, null = True)
    address = models.CharField(max_length = 200, null = True)
    date_created = models.DateTimeField(auto_now_add = True, null = True)

    def __str__(self):
        return self.name """

class Restaurant(models.Model):
    name = models.CharField(max_length = 200, null = True)
    address = models.CharField(max_length = 200, null = True)
    owner_id = models.CharField(max_length = 200, null = True)

    def __str__(self):
        return self.name


class Food(models.Model):
    name = models.CharField(max_length = 200, null = True)
    price = models.CharField(max_length = 10, null = True)
    description = models.CharField(max_length = 200, null = True, blank = True)
    restaurant = models.ForeignKey(Restaurant, null = True, on_delete = models.SET_NULL)

    def __str__(self):
        return self.name

class Cart(models.Model):
    user_id = models.CharField(max_length = 200, null = True)
    food = models.ForeignKey(Food, null = True, on_delete = models.SET_NULL)
    amount = models.CharField(max_length = 200, null = True)
    sum_price = models.CharField(max_length = 200, null = True)

    def __str__(self):
        return self.user_id + ' - ' + self.food.name

""" 
class Order(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Out of delivery', 'Out of delivery'),
        ('Delivered', 'Delivered')
    )

    food = models.ForeignKey(Food, null = True, on_delete = models.SET_NULL)
    customer = models.ForeignKey(Customer, null = True, on_delete = models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add = True, null = True)
    status = models.CharField(max_length = 200, null = True, choices = STATUS)

    def __str__(self):
        return self.customer.name + '\'s order' 
"""