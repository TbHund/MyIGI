from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from ..forms import UserRegistrationForm, BookingForm, ReviewForm
from ..models import Client, Room, RoomCategory, Promotion

class UserRegistrationFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'middle_name': 'Middle',
            'email': 'test@example.com',
            'birth_date': '1990-01-01',
            'phone': '+375 (29) 123-45-67',
            'has_child': True,
            'comments': 'Test comment',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_birth_date(self):
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'birth_date': (date.today() - timedelta(days=365*17)).strftime('%Y-%m-%d'),
            'phone': '+375 (29) 123-45-67',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('birth_date', form.errors)

    def test_invalid_phone(self):
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'birth_date': '1990-01-01',
            'phone': '123456789',  # Неверный формат
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

class BookingFormTest(TestCase):
    def setUp(self):
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
        self.promotion = Promotion.objects.create(
            code='TEST10',
            description='Test promotion',
            discount_percent=10,
            valid_from=timezone.now(),
            valid_until=timezone.now() + timedelta(days=30),
            is_active=True
        )

    def test_valid_booking(self):
        form_data = {
            'check_in_date': (timezone.now() + timedelta(days=1)).date(),
            'check_out_date': (timezone.now() + timedelta(days=3)).date(),
            'comments': 'Test booking',
            'promo_code': 'TEST10'
        }
        form = BookingForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_dates(self):
        # Дата выезда раньше даты заезда
        form_data = {
            'check_in_date': timezone.now().date() + timedelta(days=2),
            'check_out_date': timezone.now().date() + timedelta(days=1)
        }
        form = BookingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    def test_invalid_promo_code(self):
        form_data = {
            'check_in_date': timezone.now().date() + timedelta(days=1),
            'check_out_date': timezone.now().date() + timedelta(days=3),
            'promo_code': 'INVALID'
        }
        form = BookingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('promo_code', form.errors)

class ReviewFormTest(TestCase):
    def test_valid_review(self):
        form_data = {
            'rating': 5,
            'text': 'Отличный отель!'
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_rating(self):
        form_data = {
            'rating': 6,  # Рейтинг должен быть от 1 до 5
            'text': 'Отличный отель!'
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)

    def test_empty_text(self):
        form_data = {
            'rating': 5,
            'text': ''
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('text', form.errors) 