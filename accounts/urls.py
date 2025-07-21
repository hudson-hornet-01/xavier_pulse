from django.urls import path
from .views import participant_signup, event_manager_signup, login_view, logout_view

urlpatterns = [
    path('signup/', participant_signup, name='participant_signup'),  # Public
    path('signup/hidden-event-manager/', event_manager_signup, name='event_manager_signup'),  # Hidden
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
