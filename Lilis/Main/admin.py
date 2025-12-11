from django.contrib import admin
from Accounts.models import Profile
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'run', 'phone', 'role','get_staff')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'run', 'phone', 'role__name')
    list_filter = ('role',)
    ordering = ('user__username',)
    list_select_related = ('user', 'role')