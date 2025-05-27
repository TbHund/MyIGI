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
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Room categories'

class Room(models.Model):
    number = models.CharField(max_length=10, unique=True)
    category = models.ForeignKey(RoomCategory, on_delete=models.PROTECT)
    capacity = models.PositiveIntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='rooms/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.number} ({self.category.name})"

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=19, validators=[validate_phone_number])
    birth_date = models.DateField(validators=[validate_age])
    has_child = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.get_full_name()}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.check_out_date <= self.check_in_date:
            raise ValidationError('Check-out date must be after check-in date')

    def __str__(self):
        return f"Booking {self.id} - {self.client} - {self.room}"

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
