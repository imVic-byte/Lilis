from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from Sells.models import Warehouse


class Module(models.Model):
    code = models.SlugField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

class Role(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="role")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.group.name

class RoleModulePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="module_perms")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="role_perms")
    can_view = models.BooleanField(default=False)
    can_add = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ("role", "module")

    def __str__(self):
        return f"{self.role.description} - {self.module.name} (view:{self.can_view}, add:{self.can_add}, edit:{self.can_edit}, delete:{self.can_delete})"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name="profile")
    run = models.CharField(max_length=12, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.ForeignKey("Role", on_delete=models.PROTECT, related_name="profiles", blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    per_page = models.IntegerField(default=25)
    is_new = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.run}"
    
    def get_staff(self):
        return f'{self.user.is_staff}'

    def get_is_new(self):
        return f'{self.is_new}'
    
class password_reset_token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_reset_tokens")
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Token for {self.user.username} - Used: {self.is_used}"

class Lilis(models.Model):
    rut = models.CharField(max_length=12)
    bussiness_name = models.CharField(max_length=100, verbose_name='Nombre')
    fantasy_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Nombre fantasía')
    email = models.EmailField(null=True, blank=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Teléfono')
    address = models.CharField(max_length=200, blank=True, null=True, verbose_name='Dirección')
    web_site = models.URLField(blank=True, null=True, verbose_name='Página web')

    def __str__(self):
        return f"{self.bussiness_name} - {self.rut}"