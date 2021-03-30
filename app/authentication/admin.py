from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Restaurant)
admin.site.register(Food)
admin.site.register(Cart)
admin.site.register(Order)