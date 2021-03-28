from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length = 200, null = True)
    address = models.CharField(max_length = 200, null = True)
    owner_id = models.CharField(max_length = 200, null = True)
    open_time = models.TimeField(null = True)
    close_time = models.TimeField(null = True)

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

class Order(models.Model):
    order_counter = models.CharField(max_length = 200, null = True)
    user_id = models.CharField(max_length = 200, null = True)
    food = models.ForeignKey(Food, null = True, on_delete = models.SET_NULL)
    amount = models.CharField(max_length = 200, null = True)
    sum_price = models.CharField(max_length = 200, null = True)
    customer_name = models.CharField(max_length = 200, null = True)
    phone_number = models.CharField(max_length = 200, null = True)
    address = models.CharField(max_length = 200, null = True)
    description = models.CharField(max_length = 200, blank = True, null = True)
    order_date = models.DateTimeField(auto_now_add = True, null = True)

    def __str__(self):
        return self.user_id + '\'s order ' + str(self.order_date)

