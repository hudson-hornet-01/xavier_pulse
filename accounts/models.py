from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime

class CustomUser(AbstractUser):
    PARTICIPANT = 'participant'
    EVENT_MANAGER = 'event_manager'
    ADMIN = 'admin'

    USER_TYPES = (
        (PARTICIPANT, 'Participant'),
        (EVENT_MANAGER, 'Event Manager'),
        (ADMIN, 'Admin'),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPES, default=PARTICIPANT)

    full_name = models.CharField(max_length=100, null=True, blank=True)
    mobile = models.CharField(max_length=15, null=True, blank=True)
    roll_no = models.PositiveIntegerField(null=True, blank=True)
    admission_year = models.PositiveIntegerField(null=True, blank=True)
    stream = models.CharField(max_length=50, blank=True, null=True)


    def __str__(self):
        return self.full_name if self.full_name else self.username

    @property
    def current_year(self):
        if self.admission_year:
            today = datetime.date.today()
            academic_start_month = 7  # July

            if today.month >= academic_start_month:
                return (today.year - self.admission_year) + 1
            else:
                return (today.year - self.admission_year)
        return None

