from rest_framework import serializers
from .models import Event, EventAttendance
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class EventSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    attendees = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'creator', 'attendees']

class EventAttendanceSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = EventAttendance
        fields = ['id', 'event', 'user', 'status']
