from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from ..models import Client, Room, RoomCategory, Booking, Review, Promotion

class ClientModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        self.client_user = Client.objects.create(
            user=self.user,
            middle_name='Middle',
            birth_date='1990-01-01',
            phone_number='+375 (29) 123-45-67',
            has_child=True,
            comments='Test comment'
        )

    def test_client_str(self):
        expected = f"{self.user.last_name} {self.user.first_name} {self.client_user.middle_name}"
        self.assertEqual(str(self.client_user), expected.strip())

    def test_get_full_name(self):
        expected = f"{self.user.last_name} {self.user.first_name} {self.client_user.middle_name}"
        self.assertEqual(self.client_user.get_full_name(), expected.strip())

    def test_client_fields(self):
        self.assertEqual(self.client_user.user.email, 'test@example.com')
        self.assertEqual(self.client_user.phone_number, '+375 (29) 123-45-67')
        self.assertTrue(self.client_user.has_child)
        self.assertEqual(self.client_user.comments, 'Test comment')

class RoomModelTest(TestCase):
    def setUp(self):
        self.category = RoomCategory.objects.create(
            name='Люкс',
            description='Роскошный номер'
        )
        self.room = Room.objects.create(
            number='101',
            category=self.category,
            capacity=2,
            price_per_night=100.00,
            description='Тестовый номер',
            is_active=True
        )

    def test_room_str(self):
        self.assertEqual(str(self.room), f'Номер {self.room.number} ({self.category.name})')

    def test_room_fields(self):
        self.assertEqual(self.room.number, '101')
        self.assertEqual(self.room.category.name, 'Люкс')
        self.assertEqual(self.room.capacity, 2)
        self.assertEqual(float(self.room.price_per_night), 100.00)
        self.assertTrue(self.room.is_active)

class BookingModelTest(TestCase):
    def setUp(self):
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
            number='102',
            category=self.category,
            capacity=2,
            price_per_night=50.00,
            description='Тестовый номер'
        )
        self.booking = Booking.objects.create(
            client=self.client_user,
            room=self.room,
            check_in_date=timezone.now().date(),
            check_out_date=timezone.now().date() + timedelta(days=2),
            total_price=100.00,
            status='active'
        )

    def test_booking_str(self):
        expected = f"Бронь {self.booking.id} - {self.client_user} - {self.room}"
        self.assertEqual(str(self.booking), expected)

    def test_booking_duration(self):
        duration = (self.booking.check_out_date - self.booking.check_in_date).days
        self.assertEqual(duration, 2)

    def test_booking_status(self):
        self.assertEqual(self.booking.status, 'active')
        self.booking.status = 'completed'
        self.booking.save()
        self.assertEqual(self.booking.status, 'completed')

class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client_user = Client.objects.create(
            user=self.user,
            birth_date='1990-01-01',
            phone_number='+375 (29) 123-45-67'
        )
        self.review = Review.objects.create(
            client=self.client_user,
            rating=5,
            text='Отличный отель!'
        )

    def test_review_str(self):
        expected = f"Review by {self.client_user} - {self.review.rating} stars"
        self.assertEqual(str(self.review), expected)

    def test_review_fields(self):
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.text, 'Отличный отель!')

class PromotionModelTest(TestCase):
    def setUp(self):
        self.promotion = Promotion.objects.create(
            code='TEST10',
            description='Тестовая акция',
            discount_percent=10,
            valid_from=timezone.now(),
            valid_until=timezone.now() + timedelta(days=30),
            is_active=True
        )

    def test_promotion_str(self):
        expected = f"{self.promotion.code} - {self.promotion.discount_percent}% off"
        self.assertEqual(str(self.promotion), expected)

    def test_promotion_is_valid(self):
        self.assertTrue(self.promotion.is_active)
        self.assertTrue(self.promotion.valid_from <= timezone.now())
        self.assertTrue(self.promotion.valid_until >= timezone.now()) 