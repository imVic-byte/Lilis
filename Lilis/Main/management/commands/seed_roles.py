# Accounts/management/commands/seed_roles.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from Accounts.models import Role, Module, RoleModulePermission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

ROLES = [
    {"name": "Administrador", "description": "Acceso completo"},
    {"name": "Operador De Compras", "description": "Acceso limitado a compras"},
    {"name": "Operador De Ventas", "description": "Acceso limitado a ventas"},
    {"name": "Operador De Inventario", "description": "Acceso limitado a Inventario"},
    {"name": "Operador De Produccion", "description": "Acceso limitado a Produccion"},
    {"name": "Analista Financiero", "description": "Acceso limitado a Finanzas"},
]

MODULES = [
    ("products", "Products"),
    ("sells", "Sells"),
    ("accounts", "Accounts"),
]

MATRIX = {
    'Administrador': {
        'products' : 'all',
        'sells' : 'all',
        'accounts' : 'all'
    },
    'Operador De Compras': {
        'products' : 'all',
        'sells' : ('view',),
        'accounts' : ('view',)
    },
    'Operador De Ventas': {
        'products' : ('view',),
        'sells' : 'all',
        'accounts' : ('view',)
    },
    'Operador De Inventario': {
        'products' : 'all',
        'sells' : 'all',
        'accounts' : ('view',)
    },
    'Operador De Produccion': {
        'products' : ('view','change',),
        'sells' : ('view','change',),
        'accounts' : ('view',),
    },
    'Analista Financiero': {
        'products' : ('view',),
        'sells' : ('view',),
        'accounts' : ('view',),
    },  
}

SYNC_NATIVE_DJANGO_PERMS = True

APP_MODEL_MAP = {
    "sells": {
        "app_label": "sells",
        "models": ['client', 'location', 'warehouse'],
    },
    "products": {
        "app_label": "products",
        "models": ['supplier', 'rawmaterial', 'category', 'product', 'rawsupplier', 'pricehistories', 'batch'],
    },
    "accounts": {
        "app_label": "accounts",
        "models": ['profile', 'role'],
    },
    "auth": {
        "app_label":"auth",
        "models": ['user'],
    }
}

def _as_tuple(actions):
    if actions == "all":
        return {"view", "add", "change", "delete"}
    return set(actions)

def _model_perms(app_label, model, actions=("view", "add", "change", "delete")):
    try:
        ct = ContentType.objects.get(app_label=app_label, model=model)
    except ContentType.DoesNotExist:
        return Permission.objects.none()
    codenames = [f"{act}_{model}" for act in actions]
    return Permission.objects.filter(content_type=ct, codename__in=codenames)

def _sync_native_perms_for_role(group: Group, module_code: str, actions):
    if module_code not in APP_MODEL_MAP:
        return
    acts = _as_tuple(actions)
    app_label = APP_MODEL_MAP[module_code]["app_label"]
    models = APP_MODEL_MAP[module_code]["models"]

    perms = Permission.objects.none()
    for m in models:
        perms |= _model_perms(app_label, m, actions=acts)

    if perms.exists():
        group.permissions.add(*perms)

class Command(BaseCommand):
    help = "Siembra roles/módulos/matriz para Lilis y sincroniza permisos nativos para Admin."

    @transaction.atomic
    def handle(self, *args, **options):
        # 1) Módulos
        modules = {}
        for code, name in MODULES:
            m, _ = Module.objects.update_or_create(
                code=code,
                defaults={"name": name}
            )
            modules[code] = m

        # 2) Roles (Group + Role 1:1)
        groups_roles = {}
        for r in ROLES:
            if r['name'] is None:
                continue
            else:
                g, _ = Group.objects.update_or_create(name=r['name'])
                role, _ = Role.objects.update_or_create(
                    group=g,
                    
                    defaults={
                        "name": r["name"],
                        "description": r["description"]}
                )
                groups_roles[r['name']] = (g, role)

        # 3) Aplicar matriz + sincronizar permisos nativos (Admin)
        for rname, modmap in MATRIX.items():
            if rname not in groups_roles:
                continue
            group, role = groups_roles[rname]

            # Limpiar permisos nativos si vamos a resincronizar
            if SYNC_NATIVE_DJANGO_PERMS:
                group.permissions.clear()

            for mcode, actions in modmap.items():
                if mcode not in modules:
                    continue

                acts = _as_tuple(actions)
                RoleModulePermission.objects.update_or_create(
                    role=role, module=modules[mcode],
                    defaults={
                        "can_view":   "view" in acts,
                        "can_add":    "add" in acts,
                        "can_edit": "change" in acts,
                        "can_delete": "delete" in acts,
                    }
                )
                # Permisos nativos para Admin
                if SYNC_NATIVE_DJANGO_PERMS:
                    _sync_native_perms_for_role(group, mcode, actions)

            if rname == 'Administrador':
                _sync_native_perms_for_role(group,'auth','all')
            else:
                _sync_native_perms_for_role(group,'auth',('view',))

        self.stdout.write(self.style.SUCCESS("EcoEnergy: roles, módulos y matriz listos"))
        if SYNC_NATIVE_DJANGO_PERMS:
            self.stdout.write(self.style.SUCCESS("Permisos nativos sincronizados para el Admin"))
        else:
            self.stdout.write(self.style.WARNING("¡ SYNC_NATIVE_DJANGO_PERMS = False (no se asignaron permisos nativos)"))
