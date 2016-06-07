from django.contrib import admin
from .models import Address


class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'value', 'personal']


admin.site.register(Address, AddressAdmin)
admin.site.site_header = 'StartupCrate Administration'
