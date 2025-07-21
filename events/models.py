from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    registration_deadline = models.DateField(null=True, blank=True)
    time = models.TimeField()
    venue = models.CharField(max_length=255)
    is_paid = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)

    def __str__(self):
        return self.name

class PastEventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='past_images')
    image = models.ImageField(upload_to='past_event_images/')

    def __str__(self):
        return f"{self.event.name} - Past Image"
    
class Registration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    participant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="registration_set")
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    class Meta:
        unique_together = ('event', 'participant')  # Prevent duplicate registrations

    def __str__(self):
        return f"{self.participant.username} - {self.event.name} ({self.status})"

class Feedback(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="feedbacks")
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 to 5
    comment = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'participant')  # Prevent duplicate feedback
    def __str__(self):
        return f"Feedback from {self.participant.username} for {self.event.name}"