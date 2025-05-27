from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import re

def validate_phone_number(value):
    pattern = r'^\+375 \((?:29|33|44|25)\) \d{3}-\d{2}-\d{2}$'
    if not re.match(pattern, value):
        raise ValidationError('Phone number must be in format: +375 (29) XXX-XX-XX')

def validate_age(value):
    if value < 18:
        raise ValidationError('Age must be 18+')

class RoomCategory(models.Model):
    COMFORT_CHOICES = [
        ('luxury', 'Люкс'),
        ('semi_luxury', 'Полулюкс'),
        ('standard', 'Обычный'),
    ]

    name = models.CharField(max_length=100, verbose_name='Название')
    comfort_type = models.CharField(
        max_length=20, 
        choices=COMFORT_CHOICES, 
        default='standard',
        verbose_name='Тип комфортности'
    )
    description = models.TextField(verbose_name='Описание')
    price_per_night = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Цена за ночь'
    )

    def __str__(self):
        return f"{self.get_comfort_type_display()} - {self.name}"

    class Meta:
        verbose_name = 'Категория номера'
        verbose_name_plural = 'Категории номеров'

class Room(models.Model):
    number = models.CharField(max_length=10, unique=True, verbose_name='Номер комнаты')
    category = models.ForeignKey(
        RoomCategory, 
        on_delete=models.PROTECT,
        verbose_name='Категория'
    )
    capacity = models.PositiveIntegerField(verbose_name='Вместимость')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(
        upload_to='rooms/', 
        null=True, 
        blank=True,
        verbose_name='Фото номера'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    def __str__(self):
        return f"Номер {self.number} ({self.category.get_comfort_type_display()})"

    class Meta:
        verbose_name = 'Номер'
        verbose_name_plural = 'Номера'

class Client(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    middle_name = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name='Отчество'
    )
    phone_number = models.CharField(
        max_length=20,
        verbose_name='Номер телефона'
    )
    has_child = models.BooleanField(
        default=False,
        verbose_name='Есть дети'
    )
    comments = models.TextField(
        blank=True,
        verbose_name='Комментарии'
    )

    def get_full_name(self):
        full_name = f"{self.user.last_name} {self.user.first_name}"
        if self.middle_name:
            full_name += f" {self.middle_name}"
        return full_name

    def __str__(self):
        return self.get_full_name()

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

class Booking(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активно'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
    ]

    client = models.ForeignKey(
        Client, 
        on_delete=models.CASCADE,
        verbose_name='Клиент'
    )
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE,
        verbose_name='Номер'
    )
    check_in_date = models.DateField(verbose_name='Дата заезда')
    check_out_date = models.DateField(verbose_name='Дата выезда')
    actual_check_out_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name='Фактическая дата выезда'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active',
        verbose_name='Статус'
    )
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Общая стоимость'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    comments = models.TextField(
        blank=True,
        verbose_name='Комментарии'
    )

    def clean(self):
        if self.check_out_date <= self.check_in_date:
            raise ValidationError('Дата выезда должна быть позже даты заезда')

    def __str__(self):
        return f"Бронь {self.id} - {self.client} - {self.room}"

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'

class Review(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.client} - {self.rating} stars"

class Promotion(models.Model):
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    discount_percent = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def clean(self):
        if self.valid_until <= self.valid_from:
            raise ValidationError('End date must be after start date')

    def __str__(self):
        return f"{self.code} - {self.discount_percent}% off"

class CompanyInfo(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Company info'

class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='news/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'News'

class FAQ(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

    class Meta:
        verbose_name_plural = 'FAQs'

class Contact(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='contacts/')
    phone_number = models.CharField(max_length=19, validators=[validate_phone_number])
    email = models.EmailField()
    description = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.position}"

class Vacancy(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    salary_from = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_to = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Vacancies'
