from django.contrib.auth import login
from django.shortcuts import render, redirect
from .services import UserService
from django.contrib.auth.decorators import login_required
from Main.decorator import permission_or_redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from Main.utils import generate_excel_response
from Main.mixins import GroupRequiredMixin
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import RegistrarUsuarioForm

user_service = UserService()


def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if user_service.send_email(email):
            return redirect('token_verify')
        else:
            return render(request, 'password_reset.html', {'error': 'No se encontró una cuenta con ese correo electrónico.'})
    return render(request, 'password_reset.html')

def password_change(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        user = request.user
        if not user.check_password(current_password):
            return render(request, 'password_change.html', {'error': 'La contraseña actual es incorrecta.'})
        if new_password != confirm_password:
            return render(request, 'password_change.html', {'error': 'Las nuevas contraseñas no coinciden.'})
        if not user_service.validar_password(new_password):
            return render(request, 'password_change.html', {'error': 'La nueva contraseña no cumple con los requisitos de seguridad.'})            
        user.set_password(new_password)
        user.save()
        return redirect('dashboard')
    return render(request, 'password_change.html')

class RegisterView(GroupRequiredMixin, View):
    model = user_service.model
    form_class = RegistrarUsuarioForm
    template_name = 'registro.html'
    success_url = reverse_lazy('user_list')
    required_group =('Acceso Completo',)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user, contraseña = form.save()
            user_service.send_email_new_user(user, contraseña)
            return redirect(self.success_url)
        return render(request, self.template_name, {'form': form})


class UserDeleteView(GroupRequiredMixin, DeleteView):
    model = user_service.model
    success_url = reverse_lazy('user_list')
    required_group =('Acceso Completo',)
    
    def get(self, request, *args, **kwargs):
        success = user_service.delete_user(self.kwargs['id'])
        if success:
            return redirect('user_list')
        messages.error(request, "No se pudo eliminar el usuario")
        return redirect('user_list')

class UserView(GroupRequiredMixin, DetailView):
    model = user_service.model
    template_name = 'user_view.html'
    context_object_name = 'user'
    required_group =(
        'Acceso Completo',
        'Acceso limitado a Ventas',
        'Acceso limitado a Inventario',
        "Acceso limitado a Produccion",
        "Acceso limitado a Finanzas",
        "Acceso limitado a Compras"
    )


class UserListView(GroupRequiredMixin, ListView):
    required_group =('Acceso Completo',)
    model = user_service.model
    template_name = 'user_list.html'
    context_object_name = 'users'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().filter(is_active=True)
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q))
        allowed_sort_fields = ['username', 'first_name', 'profile__run', 'profile__role__group__name']
        sort_by = self.request.GET.get('sort_by', 'username') 
        order = self.request.GET.get('order', 'asc')
        if sort_by not in allowed_sort_fields:
            sort_by = 'username'
        if order not in ['asc', 'desc']:
            order = 'asc'
        order_by_field = f'-{sort_by}' if order == 'desc' else sort_by
        qs = qs.order_by(order_by_field)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.copy()
        if 'page' in query:
            del query['page']
        context['query_string'] = query.urlencode()
        q = (self.request.GET.get("q") or "").strip()
        sort_by = self.request.GET.get('sort_by', 'username')
        order = self.request.GET.get('order', 'asc')
        per_page = context['paginator'].per_page
        context.update({
            'q': q,
            'sort_by': sort_by,
            'order': order,
            'per_page': per_page,
        })
        return context
    
    def get_paginated_by(self):
        default_per_page = 25  
        allowed_per_page = [5,25,50,100]
        try:
            per_page = int(self.request.GET.get("per_page", default_per_page))
        except ValueError:
            per_page = default_per_page
        if per_page not in allowed_per_page:
            per_page = default_per_page
        return per_page

class export_users_excel(GroupRequiredMixin, View):
    required_group =('Acceso Completo',)
    
    def get(self, request):
        q = (request.GET.get("q") or "").strip()
        limit = request.GET.get("limit")
        qs = user_service.list().select_related("profile", "profile__role").order_by("username")
        if q:
            qs = qs.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(username__icontains=q) |
            Q(profile__run__icontains=q) | 
            Q(profile__role__group__name__icontains=q)
        )
        if limit:
            try:
                limit = int(limit)
                qs = qs[:limit]
            except ValueError:
                pass
        headers = [
            "Nombre de Usuario",
            "Nombre",
            "Apellido",
            "Email",
            "Run",
            "Rol",
            "¿Activo?",
            "Fecha de Creación",
        ]
        data_rows = []
        for user in qs:
            data_rows.append([
                user.username,
                user.first_name,
                user.last_name,
                user.email,
                user.profile.run if hasattr(user, 'profile') else '',
                user.profile.role.group.name if hasattr(user, 'profile') and user.profile.role else '',
                "Si" if user.is_active else "No",
                user.date_joined.strftime("%Y-%m-%d"),
            ])

        return generate_excel_response(headers, data_rows, "Lilis_Usuarios")

def token_verify(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        success, user = user_service.verify_token(token)
        if success:
            request.session['password_reset_user_id'] = user.id
            return redirect('password_recover')
        else:
            return render(request, 'token_verify.html', {'error': 'Token inválido o ya usado.'})
    return render(request, 'token_verify.html')

def password_recover(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        user_id = request.session.get('password_reset_user_id')
        if new_password != confirm_password:
            return render(request, 'password_recover.html', {'error': 'Las contraseñas no coinciden.'})
        if not user_service.validar_password(new_password):
            return render(request, 'password_recover.html', {'error': 'La nueva contraseña no cumple con los requisitos de seguridad.'})    
        if not user_id:
            return render(request, 'password_recover.html', {'error': 'Sesión expirada. Por favor, inicia el proceso nuevamente.'})    
        if user_id:
            success = user_service.password_change(user_id, new_password)
            if success:
                request.session.pop('password_reset_user_id', None)
                return redirect('login')
            else:
                return render(request, 'password_recover.html', {'error': 'Ha ocurrido un error. Inténtalo de nuevo.'})
        else:
            return render(request, 'password_recover.html', {'error': 'Sesión expirada. Por favor, inicia el proceso nuevamente.'})
    return render(request, 'password_recover.html')

@login_required
def nueva_contraseña(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        user = request.user
        if new_password != confirm_password:
            return render(request, 'nueva_contraseña.html', {'error': 'Las contraseñas no coinciden.'})
        if not user_service.validar_password(new_password):
            return render(request, 'nueva_contraseña.html', {'error': 'La nueva contraseña no cumple con los requisitos de seguridad.'})    
        user.set_password(new_password)
        user.save()
        user.profile.is_new = False
        user.profile.save()
        return redirect('dashboard')
    return render(request, 'nueva_contraseña.html')

class RoleChanger(GroupRequiredMixin, View):
    template_name = 'role_changer.html'
    form_class = user_service.role_form_class
    required_group = (
        "Acceso Completo",
    )

    def get(self, request):
        user_id = request.GET.get("user_id")
        field_name = request.GET.get("field_name")
        previous_data = request.GET.get("previous_data")
        form = self.form_class(initial={'role': previous_data})
        return render(request, self.template_name, {"form": form, "field_name": field_name, "previous_data": previous_data})

    def post(self, request):
        user_id = request.GET.get("user_id")
        field_name = request.GET.get("field_name")
        previous_data = request.GET.get("previous_data")
        form = self.form_class(request.POST)
        role = user_service.roles.objects.get(id=request.POST.get("groups"))
        success = user_service.edit_field(user_id, field_name, role)
        if success:
            return redirect('user_view', pk=user_id)
        else:
            render(request, "role_changer.html", {'form':form, "error": "No se pudo cambiar el rol."})


def edit_field(request):
    user_id = request.GET.get("user_id")
    field_name = request.GET.get("field_name")
    previous_data = request.GET.get("previous_data")
    if request.method == "POST":
        form = user_service.update_field_form_class(request.POST)
        if form.is_valid():
            success = user_service.edit_field(user_id, form.cleaned_data["field_name"], form.cleaned_data["new_data"])
            if success:
                return redirect('user_view', pk=user_id)
    else:
        form = user_service.update_field_form_class(
            initial={'field_name': field_name, 'new_data': previous_data}
        )
    return render(
        request, 
        "edit_field.html", 
        {"field_name": field_name, "previous_data": previous_data, 'form': form}
    )

def user_picture(request, id):
    if request.method == "POST":
        photo = request.FILES.get("photo")
        if photo:
            print(request.FILES)
            user_service.change_user_picture(id, photo)
            return redirect('user_view', pk=id)
        else:
            return render(request, "user_picture.html", {"error": "No se pudo cargar la foto."})
    else:
        photo = user_service.obtain_user_picture(id)
    return render(request, "user_picture.html", {"photo": photo, "id": id})
