from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Event, EventAttendance, User
from .serializers import EventSerializer, EventAttendanceSerializer
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import Http404
from rest_framework.exceptions import ValidationError

class CreateEventView(APIView):
    @method_decorator(login_required)
    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetEventView(APIView):
    @method_decorator(login_required)
    def get(self, request, pk):
        try:
            event = Event.objects.get(pk=pk)
            if event.creator != request.user:
                raise Http404("You do not have permission to access this event.")
            return Response(EventSerializer(event).data)
        except Event.DoesNotExist:
            raise Http404("Event not found")

class UpdateEventView(APIView):
    @method_decorator(login_required)
    def put(self, request, pk):
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_superuser and event.creator != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = EventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            updated_event = serializer.save()
            return Response(EventSerializer(updated_event).data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteEventView(APIView):
    @method_decorator(login_required)
    def delete(self, request, pk):
        try:
            event = Event.objects.get(pk=pk)
            if event.creator != request.user:
                raise Http404("You do not have permission to delete this event.")
            event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Event.DoesNotExist:
            raise Http404("Event not found")

class AddAttendeeView(APIView):
    def post(self, request, event_id):
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user_id = request.data.get('user_id')
        if not user_id:
            raise ValidationError("User ID is required")

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise ValidationError("User not found")

        attendance = EventAttendance(event=event, user=user)
        attendance.save()

        serializer = EventAttendanceSerializer(attendance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class RemoveAttendeeView(APIView):
    def delete(self, request, event_id, user_id):
        try:
            attendance = EventAttendance.objects.get(event__id=event_id, user__id=user_id)
        except EventAttendance.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        attendance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class EventListView(APIView):
    @method_decorator(login_required)
    def get(self, request):
        events = Event.objects.filter(creator=request.user)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

class EventDetailView(APIView):
    @method_decorator(login_required)
    def get(self, request, pk):
        try:
            event = Event.objects.get(pk=pk)
            if event.creator != request.user:
                raise Http404("You do not have permission to access this event.")
            serializer = EventSerializer(event)
            return Response(serializer.data)
        except Event.DoesNotExist:
            raise Http404("Event not found")