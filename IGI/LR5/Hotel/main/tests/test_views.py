from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from ..models import (
    Client as HotelClient, Room, RoomCategory, Booking, Review, 
    Promotion, News, FAQ, Contact, Vacancy, CompanyInfo
)
from decimal import Decimal

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        self.hotel_client = HotelClient.objects.create(
            user=self.user,
            birth_date='1990-01-01',
            phone_number='+375 (29) 123-45-67'
        )
        # Создаем категорию и номер
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

    def test_home_view(self):
        # Создаем тестовые данные
        news = News.objects.create(
            title='Test News',
            content='Test Content',
            is_published=True
        )
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/home.html')
        self.assertIn('latest_news', response.context)
        self.assertIn('rooms', response.context)
        
        # Тестируем фильтры
        response = self.client.get(reverse('home'), {'category': self.category.slug})
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('home'), {'capacity': '2'})
        self.assertEqual(response.status_code, 200)

    def test_about_view(self):
        company_info = CompanyInfo.objects.create(
            title='Test Hotel',
            content='Test Description'
        )
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/about.html')
        self.assertIn('company_info', response.context)

    def test_news_views(self):
        # Создаем тестовую новость
        news = News.objects.create(
            title='Test News',
            content='Test Content',
            is_published=True
        )
        
        # Тест списка новостей
        response = self.client.get(reverse('news'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/news_list.html')
        
        # Тест деталей новости
        response = self.client.get(reverse('news_detail', args=[news.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/news_detail.html')

    def test_faq_view(self):
        faq = FAQ.objects.create(
            question='Test Question',
            answer='Test Answer'
        )
        response = self.client.get(reverse('faq'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/faq.html')
        self.assertIn('faqs', response.context)

    def test_contacts_view(self):
        contact = Contact.objects.create(
            name='Test Contact',
            position='Manager',
            email='test@example.com',
            phone_number='+375 (29) 123-45-67',
            description='Test description'
        )
        response = self.client.get(reverse('contacts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/contacts.html')
        self.assertIn('contacts', response.context)

    def test_vacancies_views(self):
        # Создаем тестовую вакансию
        vacancy = Vacancy.objects.create(
            title='Test Vacancy',
            description='Test Description',
            requirements='Test Requirements',
            salary_from=1000.00,
            salary_to=2000.00,
            is_active=True
        )
        
        # Тест списка вакансий
        response = self.client.get(reverse('vacancies'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/vacancies.html')

    def test_reviews_views(self):
        # Тест списка отзывов
        response = self.client.get(reverse('reviews'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/reviews.html')
        
        # Тест добавления отзыва (неавторизованный)
        response = self.client.get(reverse('add_review'))
        self.assertEqual(response.status_code, 302)  # редирект на регистрацию
        
        # Тест добавления отзыва (авторизованный)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add_review'), {
            'rating': 5,
            'text': 'Great hotel!'
        })
        self.assertEqual(response.status_code, 302)  # редирект после успешного добавления
        
        # Тест отзывов по рейтингу
        response = self.client.get(reverse('reviews_by_rating', args=[5]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/reviews.html')

    def test_login_views(self):
        # Тест страницы входа
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/login.html')
        
        # Тест входа с правильными данными
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # редирект после успешного входа
        
        # Тест входа с неправильными данными
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)

    def test_registration_view(self):
        # Тест GET запроса страницы регистрации
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/register.html')
        
        # Тест POST запроса регистрации
        response = self.client.post(reverse('register'), {
            'email': 'new@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'birth_date': '1990-01-01',
            'phone': '+375 (29) 123-45-67'
        }, follow=True)
        
        # Проверяем, что пользователь был создан
        self.assertTrue(User.objects.filter(username='new@example.com').exists())
        # Проверяем, что клиент был создан
        self.assertTrue(HotelClient.objects.filter(user__username='new@example.com').exists())
        # Проверяем редирект на домашнюю страницу
        self.assertRedirects(response, reverse('home'))

    def test_profile_views(self):
        self.client.login(username='testuser', password='testpass123')
        
        # Тест профиля
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/profile.html')
        
        # Тест бронирований в профиле
        response = self.client.get(reverse('profile_bookings', args=['active']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/profile_bookings.html')

    def test_staff_views(self):
        self.client.login(username='testuser', password='testpass123')
        
        # Тест доступа обычного пользователя
        response = self.client.get(reverse('staff_bookings'))
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Делаем пользователя сотрудником
        self.hotel_client.is_staff = True
        self.hotel_client.save()
        
        # Тест просмотра бронирований
        response = self.client.get(reverse('staff_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/staff/bookings.html')
        
        # Тест с фильтрами
        response = self.client.get(reverse('staff_bookings'), {
            'status': 'active',
            'date_from': '2024-03-01',
            'date_to': '2024-03-31'
        })
        self.assertEqual(response.status_code, 200)
        
        # Тест просмотра клиентов
        response = self.client.get(reverse('staff_clients'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/staff/clients.html')
        
        # Тест с поиском клиентов
        response = self.client.get(reverse('staff_clients'), {
            'search': 'Test',
            'has_child': 'true'
        })
        self.assertEqual(response.status_code, 200)

    def test_book_room_view_unauthorized(self):
        response = self.client.get(reverse('book_room', args=[self.room.id]))
        # Должен перенаправить на страницу входа
        self.assertEqual(response.status_code, 302)

    def test_book_room_view_authorized(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('book_room', args=[self.room.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/book_room.html')

    def test_booking_process(self):
        self.client.login(username='testuser', password='testpass123')
        # Создаем тестовое бронирование
        booking_data = {
            'check_in_date': (timezone.now() + timedelta(days=1)).date(),
            'check_out_date': (timezone.now() + timedelta(days=3)).date(),
            'comments': 'Test booking'
        }
        response = self.client.post(reverse('book_room', args=[self.room.id]), booking_data)
        self.assertEqual(response.status_code, 302)  # Редирект после успешного бронирования
        self.assertTrue(Booking.objects.filter(client=self.hotel_client).exists())

    def test_cancel_booking(self):
        self.client.login(username='testuser', password='testpass123')
        # Создаем тестовое бронирование
        booking = Booking.objects.create(
            client=self.hotel_client,
            room=self.room,
            check_in_date=timezone.now().date() + timedelta(days=5),
            check_out_date=timezone.now().date() + timedelta(days=7),
            total_price=200.00,
            status='active'
        )
        response = self.client.get(reverse('cancel_booking', args=[booking.id]))
        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')

    def test_edit_profile(self):
        self.client.login(username='testuser', password='testpass123')
        
        # Тест GET запроса
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/edit_profile.html')
        
        # Тест POST запроса с валидными данными
        response = self.client.post(reverse('edit_profile'), {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'phone_number': '+375 (29) 123-45-67',
            'middle_name': 'Middle',
            'has_child': True,
            'comments': 'Updated comments'
        })
        self.assertEqual(response.status_code, 302)
        self.hotel_client.refresh_from_db()
        self.assertEqual(self.hotel_client.user.first_name, 'Updated')
        self.assertEqual(self.hotel_client.phone_number, '+375 (29) 123-45-67')

    def test_staff_booking_management(self):
        # Делаем пользователя сотрудником
        self.hotel_client.is_staff = True
        self.hotel_client.save()
        self.client.login(username='testuser', password='testpass123')
        
        # Создаем тестовое бронирование
        booking = Booking.objects.create(
            client=self.hotel_client,
            room=self.room,
            check_in_date=timezone.now().date() + timedelta(days=1),
            check_out_date=timezone.now().date() + timedelta(days=3),
            total_price=200.00,
            status='pending'
        )
        
        # Тест подтверждения бронирования
        response = self.client.post(
            reverse('staff_booking_detail', args=[booking.id]),
            {'action': 'change_status', 'status': 'active'}
        )
        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'active')
        
        # Тест отмены бронирования
        response = self.client.post(
            reverse('staff_booking_detail', args=[booking.id]),
            {'action': 'change_status', 'status': 'cancelled'}
        )
        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')