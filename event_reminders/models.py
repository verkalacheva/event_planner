from django.db import models
from django.contrib.auth.models import User
from events_app.models import Event

class Reminder(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reminder_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ], default='sent')

    def __str__(self):
        return f"{self.user.username} reminder for {self.event.title}"