from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Client, Booking
from datetime import date
from django.utils import timezone

class UserRegistrationForm(UserCreationForm):
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    middle_name = forms.CharField(max_length=30, required=False, label='Отчество')
    email = forms.EmailField(required=True, label='Email')
    phone = forms.CharField(
        max_length=20, 
        required=True, 
        label='Номер телефона',
        help_text='Введите номер телефона'
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
                 'phone', 'has_child', 'comments', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        # Генерируем username из email
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Создаем профиль клиента
            Client.objects.create(
                user=user,
                middle_name=self.cleaned_data.get('middle_name', ''),
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

    class Meta:
        model = Booking
        fields = ['check_in_date', 'check_out_date', 'comments']

    def clean(self):
        cleaned_data = super().clean()
        check_in_date = cleaned_data.get('check_in_date')
        check_out_date = cleaned_data.get('check_out_date')

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

        return cleaned_data 