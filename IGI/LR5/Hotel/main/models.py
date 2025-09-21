from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import re
from django.utils.text import slugify
from datetime import date

def validate_phone_number(value):
    pattern = r'^\+375 \((?:29|33|44|25)\) \d{3}-\d{2}-\d{2}$'
    if not re.match(pattern, value):
        raise ValidationError('Номер телефона должен быть в формате: +375 (29) XXX-XX-XX')

def validate_age(birth_date):
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    if age < 18:
        raise ValidationError('Вам должно быть не менее 18 лет.')

class RoomCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='URL-идентификатор', null=True, blank=True)
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория номера'
        verbose_name_plural = 'Категории номеров'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            counter = 1
            while RoomCategory.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)

class Room(models.Model):
    number = models.CharField(max_length=10, unique=True, verbose_name='Номер комнаты')
    category = models.ForeignKey(
        RoomCategory, 
        on_delete=models.PROTECT,
        verbose_name='Категория'
    )
    capacity = models.PositiveIntegerField(verbose_name='Вместимость')
    description = models.TextField(verbose_name='Описание')
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена за ночь'
    )
    image = models.ImageField(
        upload_to='rooms/', 
        null=True, 
        blank=True,
        verbose_name='Фото номера'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    def __str__(self):
        return f"Номер {self.number} ({self.category.name})"

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
    birth_date = models.DateField(
        validators=[validate_age],
        verbose_name='Дата рождения',
        null=True,
        blank=True
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
    is_staff = models.BooleanField(
        default=False,
        verbose_name='Сотрудник'
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

    #каскад - по удалению удаляется ВСЕ
    #при удалении клиента из бд удалятся все его брони
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
    promotion = models.ForeignKey(
        'Promotion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Использованный промокод'
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
    logo = models.ImageField(
        upload_to='company/logo/',
        verbose_name='Logo',
        blank=True,
        null=True
    )
    video_file = models.FileField(
        upload_to='company/videos/',
        verbose_name='VideoFile',
        blank=True,
        null=True,
        help_text='MP4, WebM, OGG'
    )
    #реквизиты
    inn = models.CharField(max_length=12, verbose_name='INN', blank=True)
    legal_address = models.TextField(verbose_name='Address', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Phone', blank=True)
    email = models.EmailField(verbose_name='Email', blank=True)
    
    history = models.TextField(
            verbose_name='Company History',
            blank=True,
            help_text='New line - new event. FORMAT[year: description]'
        )
    updated_at = models.DateTimeField(auto_now=True)

    def get_history_items(self):
        if not self.history:
            return []
        
        items = []
        for line in self.history.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if ':' in line:
                year, event = line.split(':', 1)
                items.append({
                    'year': year.strip(),
                    'event': event.strip()
                })
            else:
                items.append({
                    'year': '',
                    'event': line.strip()
                })
        return items
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Company info'
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
