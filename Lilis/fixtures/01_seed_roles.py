import os, sys
import django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lilis.settings')
sys.path.append(BASE_DIR)
django.setup()

from django.contrib.auth.models import Group
from Accounts.models import Role, Module, RoleModulePermission

ROLES = [
    {"name": "Administrador", "description": "Acceso completo"},
    {"name": "Operador De Compras", "description": "Acceso limitado a compras"},
    {"name": "Operador De Ventas", "description": "Acceso limitado a ventas"},
    {"name": "Operador De Inventario", "description": "Acceso limitado a Inventario"},
    {"name": "Operador De Produccion", "description": "Acceso limitado a Produccion"},
    {"name": "Analista Financiero", "description": "Acceso limitado a Finanzas"},
]

MODULES = [
    ("operacion", "Operación"),
    ("catalogo", "Catálogo"),
    ("organizacion", "Organización"),
]

for role_data in ROLES:
    group, _ = Group.objects.get_or_create(name=role_data['name'])
    role, created = Role.objects.get_or_create(
        name=role_data['name'],
        defaults={
            'description' : role_data['description'],
            'group': group,
            'privilege_level':0,
        }
    )
    if created:
        print(f"Rol creado: {role.name}")
for code, name in MODULES:
    module, _ = Module.objects.get_or_create(code=code, defaults={'name':name})
    print(f'modulo creado: {module.name}')
for role in Role.objects.all():
        for module in Module.objects.all():
            perm, created = RoleModulePermission.objects.get_or_create(
                role=role,
                module=module,
                defaults={
                    'can_view': True,
                    'can_add': True,
                    'can_edit': True,
                    'can_delete': True,
                }
            )
            if created:
                print(f'Permiso creado: {perm}')