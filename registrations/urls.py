from django.urls import path
from .views import view_registered_participants

urlpatterns = [
    path("event/<int:event_id>/participants/", view_registered_participants, name="view_registered_participants"),
]
