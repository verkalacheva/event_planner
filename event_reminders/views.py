from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Reminder
from .serializers import ReminderSerializer
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import Http404
from rest_framework.exceptions import ValidationError
from events_app.models import Event, User
from events_app.serializers import EventSerializer
from events_app.views import CreateEventView, GetEventView, UpdateEventView, DeleteEventView

class CreateReminderView(APIView):
    @method_decorator(login_required)
    def post(self, request):
        serializer = ReminderSerializer(data=request.data)
        if serializer.is_valid():
            reminder_data = serializer.validated_data
            event_id = reminder_data['event'].pk

            # Проверяем существование события через API events_app
            try:
                event_view = GetEventView()
                event_response = event_view.get(request, pk=event_id)
                if event_response.status_code != status.HTTP_200_OK:
                    raise Exception("Event not found or permission denied")
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetRemindersView(APIView):
    @method_decorator(login_required)
    def get(self, request):
        reminders = Reminder.objects.filter(user=request.user)
        serializer = ReminderSerializer(reminders, many=True)
        return Response(serializer.data)

class UpdateReminderStatusView(APIView):
    @method_decorator(login_required)
    def put(self, request, pk):
        try:
            reminder = Reminder.objects.get(pk=pk)
            if reminder.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
        except Reminder.DoesNotExist:
            raise Http404("Reminder not found")

        serializer = ReminderSerializer(reminder, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            updated_reminder = serializer.save()
            return Response(ReminderSerializer(updated_reminder).data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetEventRemindersView(APIView):
    @method_decorator(login_required)
    def get(self, request, event_id):
        try:
            # Используем API events_app для проверки доступа к событию
            event_view = GetEventView()
            event_response = event_view.get(request, pk=event_id)
            if event_response.status_code != status.HTTP_200_OK:
                return Response(event_response.data, status=event_response.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        reminders = Reminder.objects.filter(event=event_id, user=request.user)
        serializer = ReminderSerializer(reminders, many=True)
        return Response(serializer.data)

class DeleteReminderView(APIView):
    @method_decorator(login_required)
    def delete(self, request, pk):
        try:
            reminder = Reminder.objects.get(pk=pk)
            if reminder.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            reminder.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Reminder.DoesNotExist:
            raise Http404("Reminder not found")