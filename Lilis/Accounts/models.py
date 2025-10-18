from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

class Module(models.Model):
    code = models.SlugField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

class Role(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="role")
    #name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    privilege_level = models.IntegerField(default=0)


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
        return f"{self.role.name} - {self.module.name} (view:{self.can_view}, add:{self.can_add}, edit:{self.can_edit}, delete:{self.can_delete})"
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    run = models.CharField(max_length=12, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.ForeignKey("Role", on_delete=models.PROTECT, related_name="profiles")

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.run}"
    
    def get_staff(self):
        return f'{self.user.is_staff}'
    
