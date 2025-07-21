from django.urls import path
from .views import (
    home, create_event, delete_event,my_events, register_event, edit_event, manage_events, event_details,manage_event,manage_users,edit_user,delete_user, view_pending_registrations, approve_reject_participant,manage_registrations,accepted_participants,approve_participant,reject_participant,remove_participant,download_participants_pdf,submit_feedback,view_feedback
    )

urlpatterns = [
    # Home and event browsing
    path('', home, name='home'),
    path('events/', home, name='event_list'),
    path('event/<int:event_id>/', event_details, name='event_details'),

    # Event Registration & Management
    path('register-event/<int:event_id>/', register_event, name='register_event'),
    # path('unregister-event/<int:event_id>/', unregister_event, name='unregister_event'),
    path('my-events/', my_events, name='my_events'),
    path('event/<int:event_id>/pending-registrations/', view_pending_registrations, name='view_pending_registrations'),
    path('registration/<int:registration_id>/<str:action>/', approve_reject_participant, name='approve_reject_participant'),


    # Event Creation & Editing (for event managers/admins)
    path('create/', create_event, name='create_event'),
    path('edit-event/<int:event_id>/', edit_event, name='edit_event'),
    path('delete-event/<int:event_id>/', delete_event, name='delete_event'),

    # Manage Events
    path('manage-events/', manage_events, name='manage_events'),
    path("event/<int:event_id>/manage/", manage_event, name="manage_event"),
    path("event/<int:event_id>/details/", event_details, name="event_details"),
    
    # Manage Users
    path('manage-users/', manage_users, name='manage_users'),
    path('edit-user/<int:user_id>/', edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', delete_user, name='delete_user'),
    
    path('event/<int:event_id>/manage-registrations/', manage_registrations, name='manage_registrations'),
    path('event/<int:event_id>/accepted-participants/', accepted_participants, name='accepted_participants'),
    path('event/<int:event_id>/approve/<int:reg_id>/', approve_participant, name='approve_participant'),
    path('event/<int:event_id>/reject/<int:reg_id>/', reject_participant, name='reject_participant'),
    path('event/<int:event_id>/remove/<int:reg_id>/', remove_participant, name='remove_participant'),

    path('events/<int:event_id>/download_pdf/', download_participants_pdf, name='download_participants_pdf'),
    path('event/<int:event_id>/feedback/',submit_feedback, name='submit_feedback'),
    path('event/<int:event_id>/view-feedback/', view_feedback, name='view_feedback'),


]
