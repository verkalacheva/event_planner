import datetime

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Reminder
from events_app.models import Event
from django.contrib.auth import get_user_model

User = get_user_model()

class IntegrationTests(TestCase):

    def setUp(self):
        # Создаем пользователей
        self.user1 = User.objects.create_user(username='testuser1', password='testpass123')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass123')
        self.admin = User.objects.create_superuser(username='admin', password='testpass123')

        # Авторизуем клиента
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

        # Создаем несколько событий
        self.events = []
        for i in range(5):
            event = Event.objects.create(
                title=f'Test Event {i}',
                description=f'Description of Test Event {i}',
                date='2024-12-31 23:59:59',
                creator=self.user1
            )
            self.events.append(event)

    def test_integration_create_reminder(self):
        url = reverse('create_reminder')
        event = self.events[0]
        data = {
            'event': event.id,
            'reminder_time': '2024-01-01 00:00:00',
            'status': 'pending'
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        reminder = Reminder.objects.filter(event=event.id, user=self.user1.pk).first()
        self.assertIsNotNone(reminder)
        expected_time = datetime.datetime(2024, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
        self.assertEqual(reminder.reminder_time, expected_time)

        self.assertEqual(reminder.status, 'pending')

    def test_integration_create_reminder_no_event(self):
        url = reverse('create_reminder')

        data = {
            'event': 9999,
            'reminder_time': '2024-01-01 00:00:00',
            'status': 'pending'
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        reminder = Reminder.objects.filter(event=9999, user=self.user1.pk).first()
        self.assertIsNone(reminder)

    def test_integration_get_reminders(self):
        event = self.events[0]
        Reminder.objects.create(
            event = event,
            reminder_time = '2024-01-03 00:00:00',
            status = 'pending',
            user = self.user1
        )

        reminders_url = reverse('get_reminders')
        reminders_response = self.client.get(reminders_url)
        self.assertEqual(reminders_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(reminders_response.data), 1)

    def test_integration_update_reminder_status(self):
        event = self.events[0]
        reminder = Reminder.objects.create(
            event = event,
            reminder_time = '2024-01-03 00:00:00',
            status = 'pending',
            user = self.user1
        )

        reminder_id = reminder.id

        update_url = reverse('update_reminder_status', kwargs={'pk': reminder_id})
        data = {'status': 'delivered'}
        self.client.put(update_url, data)

        updated_reminder = Reminder.objects.get(id=reminder_id)
        self.assertEqual(updated_reminder.status, 'delivered')

    def test_integration_create_reminder_permission_denied(self):
        url = reverse('create_reminder')
        event = self.events[0]
        data = {
            'event': event.pk,
            'reminder_time': '2024-01-04 00:00:00',
            'status': 'pending'
        }
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_integration_get_event_reminders(self):
        event1 = self.events[0]
        event2 = self.events[1]
        Reminder.objects.create(
            event = event1,
            reminder_time = '2024-01-03 00:00:00',
            status = 'pending',
            user = self.user1
        )

        Reminder.objects.create(
            event = event2,
            reminder_time = '2024-01-03 00:00:00',
            status = 'pending',
            user = self.user1
        )
        reminders_url = reverse('get_event_reminders', kwargs={'event_id': event1.pk})
        reminders_response = self.client.get(reminders_url)
        self.assertEqual(reminders_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(reminders_response.data), 1)

    def test_integration_delete_reminder(self):
        event = self.events[0]
        reminder = Reminder.objects.create(
            event = event,
            reminder_time = '2024-01-03 00:00:00',
            status = 'pending',
            user = self.user1
        )
        reminder_id = reminder.pk

        delete_url = reverse('delete_reminder', kwargs={'pk': reminder_id})
        delete_response = self.client.delete(delete_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        reminders = Reminder.objects.filter(id=reminder_id)
        self.assertEqual(len(reminders), 0)
