from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from unittest.mock import patch
from ..api_utils import get_random_dog, get_random_cat_fact
from ..models import Client, Room, RoomCategory, Booking
from datetime import timedelta

class UtilsTest(TestCase):
    def setUp(self):
        # Создаем тестового пользователя и клиента для тестов бронирования
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client_user = Client.objects.create(
            user=self.user,
            birth_date='1990-01-01',
            phone_number='+375 (29) 123-45-67'
        )
        self.category = RoomCategory.objects.create(
            name='Стандарт',
            description='Стандартный номер'
        )
        self.room = Room.objects.create(
            number='101',
            category=self.category,
            capacity=2,
            price_per_night=100.00,
            description='Тестовый номер'
        )

    def test_get_common_context(self):
        from ..views import get_common_context
        context = get_common_context()
        self.assertIn('random_dog', context)
        self.assertIn('cat_fact', context)
        self.assertIn('current_time', context)
        self.assertIn('utc_time', context)
        self.assertIn('user_timezone', context)
        self.assertIn('calendar', context)

    @patch('requests.get')
    def test_api_utils_success(self, mock_get):
        # Тестируем успешное получение случайной собаки
        mock_get.return_value.json.return_value = {
            'status': 'success',
            'message': 'https://images.dog.ceo/breeds/poodle-standard/n02113799_1057.jpg'
        }
        mock_get.return_value.raise_for_status.return_value = None
        
        dog_data = get_random_dog()
        self.assertIsInstance(dog_data, dict)
        self.assertIn('image_url', dog_data)
        self.assertIn('breed', dog_data)
        self.assertTrue(dog_data['image_url'].startswith('http'))
        self.assertEqual(dog_data['breed'], 'Poodle Standard')

        # Тестируем успешное получение факта о кошках
        mock_get.return_value.json.return_value = {'fact': 'Cats are awesome'}
        cat_fact = get_random_cat_fact()
        self.assertIsInstance(cat_fact, str)
        self.assertEqual(cat_fact, 'Cats are awesome')

    @patch('requests.get')
    def test_api_utils_failure(self, mock_get):
        # Тестируем ошибку сети для get_random_dog
        mock_get.side_effect = Exception('Network error')
        dog_data = get_random_dog()
        self.assertIsNone(dog_data)

        # Тестируем ошибку сети для get_random_cat_fact
        cat_fact = get_random_cat_fact()
        self.assertIsNone(cat_fact)

        # Тестируем неверный формат ответа для get_random_dog
        mock_get.side_effect = None
        mock_get.return_value.json.return_value = {'status': 'error'}
        dog_data = get_random_dog()
        self.assertIsNone(dog_data)

    def test_booking_duration_calculation(self):
        booking = Booking.objects.create(
            client=self.client_user,  # Используем созданного клиента
            room=self.room,
            check_in_date=timezone.now().date(),
            check_out_date=timezone.now().date() + timedelta(days=3),
            total_price=300.00
        )
        duration = (booking.check_out_date - booking.check_in_date).days
        self.assertEqual(duration, 3)

    def test_room_availability(self):
        # Проверяем доступность номера
        check_in = timezone.now().date() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)
        
        # Создаем бронирование
        Booking.objects.create(
            client=self.client_user,  # Используем созданного клиента
            room=self.room,
            check_in_date=check_in,
            check_out_date=check_out,
            total_price=200.00,
            status='active'
        )
        
        # Проверяем, что номер недоступен на эти даты
        booked_rooms = Booking.objects.filter(
            room=self.room,
            check_in_date__lte=check_out,
            check_out_date__gte=check_in,
            status='active'
        )
        self.assertTrue(booked_rooms.exists())

        # Проверяем доступность на другие даты
        future_check_in = check_out + timedelta(days=1)
        future_check_out = future_check_in + timedelta(days=1)
        booked_rooms = Booking.objects.filter(
            room=self.room,
            check_in_date__lte=future_check_out,
            check_out_date__gte=future_check_in,
            status='active'
        )
        self.assertFalse(booked_rooms.exists()) 