from rest_framework import serializers
from .models import Reminder
from events_app.serializers import UserSerializer, EventSerializer

class ReminderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, required=False)
    class Meta:
        model = Reminder
        fields = ['id', 'event', 'user', 'reminder_time', 'status']