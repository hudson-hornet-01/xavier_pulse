from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import CustomUser
from .forms import EventForm,FeedbackForm
from .models import Event,Registration,PastEventImage,Feedback
from django.core.paginator import Paginator
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.utils import timezone

def home(request):
    events_list = Event.objects.all().order_by('date')  # Fetch all events
    paginator = Paginator(events_list, 6)  # Show 6 events per page

    page_number = request.GET.get('page')
    events = paginator.get_page(page_number)

    return render(request, 'events/home.html', {'events': events})

@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user  # Assign event manager
            event.save()
            
            # Handle multiple past images
            past_images = request.FILES.getlist('past_images')
            for image in past_images:
                PastEventImage.objects.create(event=event, image=image)

            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'events/create_event.html', {'form': form})

@login_required
def my_events(request):
    if request.user.user_type == 'participant':
        registrations = Registration.objects.filter(participant=request.user).select_related('event')
        registered_events = [registration.event for registration in registrations]

        return render(request, 'events/my_events.html', {'registered_events': registered_events})
    else:
        messages.error(request, "Only participants can view their registered events.")
        return redirect('home')

@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Ensure only the event creator or an admin can delete the event
    if event.created_by != request.user and request.user.user_type != 'admin':
        messages.error(request, "You do not have permission to delete this event.")
        return redirect('home')

    event.delete()
    messages.success(request, "Event deleted successfully!")
    return redirect('home')

    
    
@login_required
def event_list(request):
    if request.user.user_type == 'admin':
        events = Event.objects.all()  # Admins see all events
    elif request.user.user_type == 'event_manager':
        events = Event.objects.filter(created_by=request.user)  # Event managers see only their events
    else:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')

    return render(request, 'events/event_list.html', {'events': events})


@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Ensure only participants can register
    if request.user.user_type != 'participant':
        messages.error(request, "Only participants can register for events.")
        return redirect('home')

    if event.registration_deadline and timezone.now().date() > event.registration_deadline:
        messages.error(request, "Registration for this event has closed.")
        return redirect('event_details', event_id=event.id)
    
    # Check if the user has already registered for the event
    existing_registration = Registration.objects.filter(event=event, participant=request.user).first()

    if existing_registration:
        if existing_registration.status == "approved":
            messages.warning(request, "You are already registered for this event.")
        elif existing_registration.status == "pending":
            messages.info(request, "Your registration is pending approval.")
        elif existing_registration.status == "rejected":
            messages.error(request, "Your registration was rejected. Please contact the event manager.")
        return redirect('my_events')

    # Register the user with 'pending' status for approval
    Registration.objects.create(event=event, participant=request.user, status="pending")
    messages.success(request, f"Your registration request for {event.name} has been submitted and is pending approval.")

    return redirect('my_events')


@login_required
def view_pending_registrations(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Ensure the event manager is viewing only their own event
    if event.created_by != request.user and request.user.user_type != 'admin':
        messages.error(request, "You can only manage registrations for your own events.")
        return redirect('home')

    pending_registrations = Registration.objects.filter(event=event, status='pending')
    
    return render(request, "events/pending_registrations.html", {"event": event, "pending_registrations": pending_registrations})


@login_required
def approve_reject_participant(request, registration_id, action):
    registration = get_object_or_404(Registration, id=registration_id)

    # Ensure event manager is approving for their own event
    if registration.event.created_by != request.user and request.user.user_type != 'admin':
        messages.error(request, "You do not have permission to manage this event.")
        return redirect('home')

    if action == 'approve':
        registration.status = 'approved'
        messages.success(request, f"{registration.participant.username} has been approved for {registration.event.name}.")
    elif action == 'reject':
        registration.status = 'rejected'
        messages.warning(request, f"{registration.participant.username} has been rejected from {registration.event.name}.")
    
    registration.save()
    return redirect('view_pending_registrations', event_id=registration.event.id)


@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Ensure only the event creator or an admin can edit the event
    if event.created_by != request.user and request.user.user_type != 'admin':
        messages.error(request, "You do not have permission to edit this event.")
        return redirect('home')

    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully!")
            return redirect('home')
    else:
        form = EventForm(instance=event)

    return render(request, 'events/edit_event.html', {'form': form, 'event': event})


@login_required
def manage_events(request):
    if request.user.user_type == "admin":
        events = Event.objects.all()  # Admin sees all events
    elif request.user.user_type == "event_manager":
        events = Event.objects.filter(created_by=request.user)  # Event managers see only their events
    else:
        events = Event.objects.all()  # Participants see all events but with limited options

    return render(request, "events/manage_events.html", {"events": events})


@login_required
def event_details(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    today = timezone.now().date()

    is_approved = Registration.objects.filter(event=event, participant=request.user, status='approved').exists()
    has_feedback = Feedback.objects.filter(event=event, participant=request.user).exists()

    return render(request, 'events/event_details.html', {
        'event': event,
        'today': today,
        'is_approved': is_approved,
        'has_feedback': has_feedback,
    })

@login_required
def manage_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Restrict access to event managers (only for their events) and admins
    if request.user.user_type != "admin" and event.created_by != request.user:
        return redirect("manage_events")  # Unauthorized access

    return render(request, "events/manage_event.html", {"event": event})

@login_required
def manage_users(request):
    users = CustomUser.objects.all()
    return render(request, 'events/manage_users.html', {'users': users})

@login_required
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, "User details updated successfully!")
        return redirect('manage_users')

    return render(request, 'events/edit_user.html', {'user': user})

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully!")
    return redirect('manage_users')

@login_required
def manage_registrations(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Ensure only the event manager of this event or an admin can view participants
    if event.created_by != request.user and request.user.user_type != 'admin':
        messages.error(request, "You do not have permission to manage registrations for this event.")
        return redirect('home')

    pending_registrations = Registration.objects.filter(event=event, status='pending').select_related('participant')

    return render(request, 'events/manage_registrations.html', {'event': event, 'registrations': pending_registrations})


@login_required
def accepted_participants(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if event.created_by != request.user and request.user.user_type != 'admin':
        messages.error(request, "You do not have permission to view participants for this event.")
        return redirect('home')

    approved_registrations = Registration.objects.filter(event=event, status='approved').select_related('participant')

    return render(request, 'events/accepted_participants.html', {'event': event, 'registrations': approved_registrations})

@login_required
def approve_participant(request, event_id, reg_id):
    registration = get_object_or_404(Registration, id=reg_id, event_id=event_id)
    registration.status = 'approved'
    registration.save()
    messages.success(request, "Participant approved successfully!")
    return redirect('manage_registrations', event_id=event_id)


@login_required
def reject_participant(request, event_id, reg_id):
    registration = get_object_or_404(Registration, id=reg_id, event_id=event_id)
    registration.delete()
    messages.success(request, "Participant rejected successfully!")
    return redirect('manage_registrations', event_id=event_id)

@login_required
def remove_participant(request, event_id, reg_id):
    registration = get_object_or_404(Registration, id=reg_id, event_id=event_id)
    registration.delete()
    messages.success(request, "Participant removed successfully!")
    return redirect('accepted_participants', event_id=event_id)

def download_participants_pdf(request, event_id):
    event = Event.objects.get(id=event_id)
    registrations = event.registrations.filter(status='approved')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Accepted_Participants_{event.name}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph(f"Accepted Participants for {event.name}", styles['Heading2'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    data = [['Serial No.', 'Name', 'Roll No.', 'Stream', 'Year']]

    for idx, reg in enumerate(registrations, start=1):
        data.append([
            str(idx),
            reg.participant.full_name,
            str(reg.participant.roll_no),
            reg.participant.stream,
            str(reg.participant.current_year)
        ])

    table = Table(data, colWidths=[60, 120, 80, 100, 60])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)
    doc.build(elements)
    return response

@login_required
def submit_feedback(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Check if user is eligible
    if request.user.user_type != 'participant':
        messages.error(request, "Only participants can give feedback.")
        return redirect('home')

    # Must be registered & approved
    registration = Registration.objects.filter(event=event, participant=request.user, status='approved').first()
    if not registration:
        messages.error(request, "You are not registered or approved for this event.")
        return redirect('event_details', event_id=event.id)

    # Event must be completed
    if timezone.now().date() <= event.date:
        messages.error(request, "Feedback can be submitted only after the event is completed.")
        return redirect('event_details', event_id=event.id)

    # Prevent duplicate feedback
    if Feedback.objects.filter(event=event, participant=request.user).exists():
        messages.info(request, "You have already submitted feedback.")
        return redirect('event_details', event_id=event.id)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.event = event
            feedback.participant = request.user
            feedback.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('event_details', event_id=event.id)
    else:
        form = FeedbackForm()

    return render(request, 'events/submit_feedback.html', {'form': form, 'event': event})

@login_required
def view_feedback(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.user.user_type != 'admin' and event.created_by != request.user:
        messages.error(request, "You do not have permission to view feedback for this event.")
        return redirect('home')

    feedbacks = Feedback.objects.filter(event=event).select_related('participant')

    return render(request, 'events/view_feedback.html', {
        'event': event,
        'feedbacks': feedbacks,
    })
