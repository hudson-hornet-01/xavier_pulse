from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import ParticipantSignupForm, EventManagerSignupForm

# Participant Signup View
def participant_signup(request):
    if request.method == "POST":
        form = ParticipantSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = ParticipantSignupForm()
    return render(request, 'accounts/signup.html', {'form': form, 'user_type': 'Participant'})

# Event Manager Signup View (via direct hidden link)
def event_manager_signup(request):
    if request.method == "POST":
        form = EventManagerSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('event_list')
    else:
        form = EventManagerSignupForm()
    return render(request, 'accounts/signup.html', {'form': form, 'user_type': 'Event Manager'})

# Login View
def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error = "Invalid username or password"
    return render(request, 'accounts/login.html', {'error': error})

# Logout
def logout_view(request):
    logout(request)
    return redirect('login')
