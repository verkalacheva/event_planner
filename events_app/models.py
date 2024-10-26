from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField(default=now)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    attendees = models.ManyToManyField(User, through='EventAttendance')

    def __str__(self):
        return self.title

class EventAttendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendances')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attended_events')
    status = models.CharField(max_length=20, choices=[
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('pending', 'Pending'),
    ], default='pending')

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"