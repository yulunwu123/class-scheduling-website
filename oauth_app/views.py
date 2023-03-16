from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth import get_user_model

@login_required(login_url='/users/login')
def secure(request):
    user = request.user
    return render(request, 'secure.html', {'email': user.email})