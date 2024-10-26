from django.urls import path
from .views import (CreateEventView,
                    GetEventView,
                    UpdateEventView,
                    DeleteEventView,
                    AddAttendeeView,
                    RemoveAttendeeView,
                    EventListView,
                    EventDetailView)

urlpatterns = [
    path('create/', CreateEventView.as_view(), name='create_event'),
    path('get/<int:pk>/', GetEventView.as_view(), name='get_event'),
    path('update/<int:pk>/', UpdateEventView.as_view(), name='update_event'),
    path('delete/<int:pk>/', DeleteEventView.as_view(), name='delete_event'),
    path('add_attendee/<int:event_id>/', AddAttendeeView.as_view(), name='add_attendee'),
    path('remove_attendee/<int:event_id>/<int:user_id>/', RemoveAttendeeView.as_view(), name='remove_attendee'),
    path('list/', EventListView.as_view(), name='event_list'),
    path('detail/<int:pk>/', EventDetailView.as_view(), name='event_detail'),
]