from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect,render, get_object_or_404
from events.models import Event,Registration

@login_required
def view_registered_participants(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Ensure event managers only access their own events
    if request.user.user_type == "event_manager" and event.created_by != request.user:
        return redirect("home")  # Unauthorized access

    # Fetch only approved participants for this event
    participants = Registration.objects.filter(event=event, status="approved")  

    return render(request, "registrations/registered_participants.html", {"event": event, "participants": participants})
