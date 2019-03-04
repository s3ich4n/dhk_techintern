from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


class UserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name',
        'last_name', 'is_active', 'is_staff'
    )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


