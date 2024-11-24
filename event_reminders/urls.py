from django.urls import path
from .views import (
    CreateReminderView,
    GetRemindersView,
    UpdateReminderStatusView,
    GetEventRemindersView,
    DeleteReminderView
)

urlpatterns = [
    path('reminders/', CreateReminderView.as_view(), name='create_reminder'),
    path('reminders/list/', GetRemindersView.as_view(), name='get_reminders'),
    path('reminders/<int:pk>/', UpdateReminderStatusView.as_view(), name='update_reminder_status'),
    path('events/<int:event_id>/reminders/', GetEventRemindersView.as_view(), name='get_event_reminders'),
    path('reminders/<int:pk>/delete/', DeleteReminderView.as_view(), name='delete_reminder'),
]