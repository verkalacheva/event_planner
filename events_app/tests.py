from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Event, EventAttendance

User = get_user_model()

class EventCRUDTests(TestCase):

    def setUp(self):
        # Создаем пользователей
        self.user1 = User.objects.create_user(username='testuser1', password='testpass123')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass123')
        self.admin = User.objects.create_superuser(username='admin', password='testpass123')

        self.client = APIClient()

        # Авторизуем клиента
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

    def test_create_event_successful(self):
        url = reverse('create_event')
        data = {
            'title': 'New Test Event',
            'description': 'Description of New Test Event',
            'date': '2024-12-31 23:59:59'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(Event.objects.count(), 6)

        # Проверяем, что новое событие принадлежит правильному пользователю
        new_event = Event.objects.latest('id')
        self.assertEqual(new_event.creator, self.user1)

    def test_get_event(self):
        url = reverse('get_event', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['creator']['id'], self.user1.id)

    def test_update_event_successful(self):
        event = Event.objects.create(title="Test Event", creator=self.user1)
        url = reverse('update_event', kwargs={'pk': event.id})
        data = {'title': 'Updated Title'}

        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Event.objects.get(id=event.id).title, 'Updated Title')

    def test_update_event_invalid(self):
        # Тест на невалидные данные
        event = Event.objects.create(title="Test Event", creator=self.user1)
        url = reverse('update_event', kwargs={'pk': event.id})
        invalid_data = {'date': '111'}
        response = self.client.put(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('date', response.data)

    def test_update_event_permission_denied(self):
        # Тест на отсутствие прав доступа
        event = Event.objects.create(title="Test Event", creator=self.user1)
        url = reverse('update_event', kwargs={'pk': event.id})
        data = {'title': 'Updated Title'}
        self.client.force_authenticate(user=self.user2)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_event(self):
        url = reverse('delete_event', kwargs={'pk': 1})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Event.objects.count(), 4)

    def test_add_attendee(self):
        # Создаем событие для добавления участника
        event = Event.objects.create(
            title="Test Event",
            description="Test Description",
            date="2024-12-31 23:59:59",
            creator=self.user1
        )

        url = reverse('add_attendee', kwargs={'event_id': event.id})
        data = {'user_id': self.user2.id}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EventAttendance.objects.filter(event__id=event.id, user__id=self.user2.id).count(), 1)

    def test_remove_attendee(self):
        EventAttendance.objects.create(event=self.events[0], user=self.user2)
        url = reverse('remove_attendee', kwargs={'event_id': 1, 'user_id': self.user2.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(EventAttendance.objects.filter(event__id=1, user__id=self.user2.id).count(), 0)