from django.contrib.auth.mixins import AccessMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages


class GroupRequiredMixin(AccessMixin):
    required_group = None
    permission_denied_message = ('No tienes permiso para acceder a esta página')
    permission_denied_url = reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.required_group is None:
            raise ValueError('Debe especificar un grupo')
        user_groups = [group.name for group in request.user.groups.all()]
        is_member = any(group in user_groups for group in self.required_group)
        if not is_member:
            messages.error(request, self.permission_denied_message)
            return redirect(self.permission_denied_url)
        return super().dispatch(request, *args, **kwargs)

class StaffRequiredMixin(UserPassesTestMixin):
    permission_denied_message = ('No tienes permiso para acceder a esta página')
    permission_denied_url = reverse_lazy('dashboard')

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, self.permission_denied_message)
        return redirect(self.permission_denied_url)

class IsNewUserMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.profile.is_new