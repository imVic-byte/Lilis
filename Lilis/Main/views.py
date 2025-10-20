from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required

@login_required
def dashboard(request):
    return render(request, 'main/dashboard.html')