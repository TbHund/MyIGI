from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Client, Booking, Review, Promotion
from datetime import date
from django.utils import timezone
from django.core.exceptions import ValidationError
import re

def validate_age(birth_date):
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    if age < 18:
        raise ValidationError('Вам должно быть не менее 18 лет для регистрации.')

def validate_phone_number(phone):
    pattern = r'^\+375 \((?:29|33|44|25)\) \d{3}-\d{2}-\d{2}$'
    if not re.match(pattern, phone):
        raise ValidationError('Номер телефона должен быть в формате: +375 (29) XXX-XX-XX')

class UserRegistrationForm(UserCreationForm):
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    middle_name = forms.CharField(max_length=30, required=False, label='Отчество')
    email = forms.EmailField(required=True, label='Email')
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
        label='Дата рождения',
        validators=[validate_age],
        help_text='Вам должно быть не менее 18 лет'
    )
    phone = forms.CharField(
        max_length=20, 
        required=True, 
        label='Номер телефона',
        help_text='Введите номер телефона в формате +375 (29) XXX-XX-XX',
        validators=[validate_phone_number]
    )
    has_child = forms.BooleanField(
        required=False, 
        label='Есть дети',
        initial=False
    )
    comments = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label='Комментарии'
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        label='Пароль'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        label='Подтверждение пароля'
    )

    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'middle_name', 'email', 
                 'birth_date', 'phone', 'has_child', 'comments', 
                 'password1', 'password2')

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            validate_age(birth_date)
        return birth_date

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Удаляем все нецифровые символы
            digits = ''.join(filter(str.isdigit, phone))
            if len(digits) == 12 and digits.startswith('375'):
                # Форматируем номер в нужный формат
                formatted_number = f'+375 ({digits[3:5]}) {digits[5:8]}-{digits[8:10]}-{digits[10:12]}'
                return formatted_number
            else:
                raise ValidationError('Неверный формат номера телефона')
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            Client.objects.create(
                user=user,
                middle_name=self.cleaned_data.get('middle_name', ''),
                birth_date=self.cleaned_data['birth_date'],
                phone_number=self.cleaned_data['phone'],
                has_child=self.cleaned_data.get('has_child', False),
                comments=self.cleaned_data.get('comments', '')
            )
        return user

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='Имя пользователя')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')

class BookingForm(forms.ModelForm):
    check_in_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Дата заезда',
        error_messages={
            'required': 'Пожалуйста, укажите дату заезда',
            'invalid': 'Пожалуйста, введите корректную дату заезда'
        }
    )
    check_out_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Дата выезда',
        error_messages={
            'required': 'Пожалуйста, укажите дату выезда',
            'invalid': 'Пожалуйста, введите корректную дату выезда'
        }
    )
    comments = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='Комментарии к бронированию'
    )
    promo_code = forms.CharField(
        max_length=20,
        required=False,
        label='Промокод',
        help_text='Если у вас есть промокод, введите его здесь'
    )

    class Meta:
        model = Booking
        fields = ['check_in_date', 'check_out_date', 'comments', 'promo_code']
        widgets = {
            'check_in_date': forms.DateInput(attrs={'type': 'date'}),
            'check_out_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        check_in_date = cleaned_data.get('check_in_date')
        check_out_date = cleaned_data.get('check_out_date')
        promo_code = cleaned_data.get('promo_code')

        if check_in_date and check_out_date:
            today = timezone.now().date()
            
            if check_in_date < today:
                raise forms.ValidationError(
                    'Дата заезда не может быть в прошлом'
                )
            
            if check_out_date <= check_in_date:
                raise forms.ValidationError(
                    'Дата выезда должна быть позже даты заезда'
                )
            
            # Проверяем, что бронирование не более чем на 30 дней
            if (check_out_date - check_in_date).days > 30:
                raise forms.ValidationError(
                    'Максимальный срок бронирования - 30 дней'
                )

        if promo_code:
            try:
                promotion = Promotion.objects.get(
                    code=promo_code,
                    is_active=True,
                    valid_from__lte=timezone.now(),
                    valid_until__gte=timezone.now()
                )
                cleaned_data['promotion'] = promotion
            except Promotion.DoesNotExist:
                raise ValidationError({'promo_code': 'Недействительный промокод'})

        return cleaned_data 

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Оценка от 1 до 5'
        }),
        label='Оценка'
    )
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Поделитесь своими впечатлениями',
            'rows': 4
        }),
        label='Текст отзыва'
    )

    class Meta:
        model = Review
        fields = ['rating', 'text']

class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')
    email = forms.EmailField(required=True, label='Email')
    middle_name = forms.CharField(max_length=30, required=False, label='Отчество')
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        label='Номер телефона',
        help_text='Введите номер телефона в формате +375 (29) XXX-XX-XX',
        validators=[validate_phone_number]
    )
    has_child = forms.BooleanField(
        required=False,
        label='Есть дети',
        initial=False
    )
    comments = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label='Комментарии'
    )

    class Meta:
        model = Client
        fields = ['middle_name', 'phone_number', 'has_child', 'comments']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        client = super().save(commit=False)
        
        # Обновляем данные пользователя
        user = client.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            client.save()
        
        return client 