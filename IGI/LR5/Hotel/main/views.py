from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
from decimal import Decimal
from .models import (
    News, FAQ, Contact, Vacancy, Review, 
    Promotion, CompanyInfo, Room, RoomCategory, Booking
)
from .api_utils import get_random_dog, get_random_cat_fact
from .forms import UserRegistrationForm, LoginForm, BookingForm

def get_common_context():
    """Get common context data for all pages"""
    return {
        'random_dog': get_random_dog(),
        'cat_fact': get_random_cat_fact()
    }

def home(request):
    latest_news = News.objects.filter(is_published=True).order_by('-created_at').first()
    rooms = Room.objects.filter(is_active=True)
    categories = RoomCategory.objects.all()
    
    # Фильтрация по категории
    category = request.GET.get('category')
    if category:
        rooms = rooms.filter(category__slug=category)
    
    # Фильтрация по вместимости
    capacity = request.GET.get('capacity')
    if capacity and capacity.isdigit():
        rooms = rooms.filter(capacity__gte=int(capacity))
    
    # Фильтрация по датам, если они указаны
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    
    if check_in and check_out:
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
            
            # Получаем занятые номера на указанные даты (только активные бронирования)
            booked_rooms = Booking.objects.filter(
                Q(check_in_date__lte=check_out_date) & 
                Q(check_out_date__gte=check_in_date),
                status='active'  # Учитываем только активные бронирования
            ).values_list('room_id', flat=True)
            
            # Исключаем занятые номера из списка
            rooms = rooms.exclude(id__in=booked_rooms)
        except ValueError:
            messages.error(request, 'Неверный формат даты')
    
    context = {
        'latest_news': latest_news,
        'rooms': rooms,
        'categories': categories,
        'selected_category': category,
        'selected_capacity': capacity,
        'check_in': check_in,
        'check_out': check_out,
        **get_common_context()
    }
    return render(request, 'main/home.html', context)

def about(request):
    company_info = CompanyInfo.objects.first()
    context = {
        'company_info': company_info,
        **get_common_context()
    }
    return render(request, 'main/about.html', context)

def news_list(request):
    news = News.objects.filter(is_published=True).order_by('-created_at')
    context = {
        'news': news,
        **get_common_context()
    }
    return render(request, 'main/news_list.html', context)

def news_detail(request, pk):
    news_item = get_object_or_404(News, pk=pk, is_published=True)
    context = {
        'news_item': news_item,
        **get_common_context()
    }
    return render(request, 'main/news_detail.html', context)

def faq(request):
    faqs = FAQ.objects.order_by('-created_at')
    context = {
        'faqs': faqs,
        **get_common_context()
    }
    return render(request, 'main/faq.html', context)

def contacts(request):
    contacts = Contact.objects.all()
    context = {
        'contacts': contacts,
        **get_common_context()
    }
    return render(request, 'main/contacts.html', context)

def privacy(request):
    return render(request, 'main/privacy.html', get_common_context())

def vacancies(request):
    active_vacancies = Vacancy.objects.filter(is_active=True).order_by('-created_at')
    context = {
        'vacancies': active_vacancies,
        **get_common_context()
    }
    return render(request, 'main/vacancies.html', context)

def reviews(request):
    all_reviews = Review.objects.order_by('-created_at')
    context = {
        'reviews': all_reviews,
        **get_common_context()
    }
    return render(request, 'main/reviews.html', context)

@login_required
def add_review(request):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        text = request.POST.get('text')
        if rating and text:
            Review.objects.create(
                client=request.user.client,
                rating=rating,
                text=text
            )
            messages.success(request, 'Спасибо за ваш отзыв!')
            return redirect('reviews')
    return render(request, 'main/add_review.html', get_common_context())

def promotions(request):
    active_promotions = Promotion.objects.filter(
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_until__gte=timezone.now()
    ).order_by('valid_until')
    context = {
        'promotions': active_promotions,
        **get_common_context()
    }
    return render(request, 'main/promotions.html', context)

@login_required
def profile(request):
    user_bookings = request.user.client.booking_set.all().order_by('-created_at')
    context = {
        'bookings': user_bookings,
        **get_common_context()
    }
    return render(request, 'main/profile.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешно завершена!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'main/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.first_name}!')
                return redirect('home')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = LoginForm()
    return render(request, 'main/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

def room_list(request):
    # Получаем все категории номеров
    categories = RoomCategory.objects.all()
    rooms = Room.objects.filter(is_active=True)
    
    # Фильтрация по датам, если они указаны
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    
    if check_in and check_out:
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
            
            # Получаем занятые номера на указанные даты (только активные бронирования)
            booked_rooms = Booking.objects.filter(
                Q(check_in_date__lte=check_out_date) & 
                Q(check_out_date__gte=check_in_date),
                status='active'  # Учитываем только активные бронирования
            ).values_list('room_id', flat=True)
            
            # Исключаем занятые номера из списка
            rooms = rooms.exclude(id__in=booked_rooms)
        except ValueError:
            messages.error(request, 'Неверный формат даты')
    
    context = {
        'categories': categories,
        'rooms': rooms,
        'check_in': check_in,
        'check_out': check_out,
        **get_common_context()
    }
    return render(request, 'main/room_list.html', context)

@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id, is_active=True)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.client = request.user.client
            booking.room = room
            
            # Расчет стоимости
            days = (booking.check_out_date - booking.check_in_date).days
            booking.total_price = room.category.price_per_night * Decimal(days)
            
            # Проверяем, не занят ли номер на эти даты
            conflicting_bookings = Booking.objects.filter(
                room=room,
                status='active',  # Проверяем только активные бронирования
                check_in_date__lte=booking.check_out_date,
                check_out_date__gte=booking.check_in_date
            )
            
            if conflicting_bookings.exists():
                form.add_error(None, 'Этот номер уже забронирован на выбранные даты')
            else:
                try:
                    booking.save()
                    messages.success(request, 'Номер успешно забронирован!')
                    return redirect('profile')
                except Exception as e:
                    form.add_error(None, f'Ошибка при сохранении бронирования: {str(e)}')
    else:
        # Предзаполняем даты из GET-параметров, если они есть
        initial = {}
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')
        if check_in:
            try:
                initial['check_in_date'] = datetime.strptime(check_in, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Неверный формат даты заезда')
        if check_out:
            try:
                initial['check_out_date'] = datetime.strptime(check_out, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Неверный формат даты выезда')
        form = BookingForm(initial=initial)
    
    context = {
        'form': form,
        'room': room,
        **get_common_context()
    }
    return render(request, 'main/book_room.html', context)

def news_archive(request, year, month):
    news = News.objects.filter(
        created_at__year=int(year),
        created_at__month=int(month),
        is_published=True
    ).order_by('-created_at')
    
    context = {
        'news': news,
        'year': year,
        'month': month,
        **get_common_context()
    }
    return render(request, 'main/news_archive.html', context)

def vacancies_by_category(request, category):
    vacancies = Vacancy.objects.filter(
        category=category,
        is_active=True
    ).order_by('-created_at')
    
    context = {
        'vacancies': vacancies,
        'category': category,
        **get_common_context()
    }
    return render(request, 'main/vacancies.html', context)

def reviews_by_rating(request, rating):
    reviews = Review.objects.filter(
        rating=rating
    ).order_by('-created_at')
    
    context = {
        'reviews': reviews,
        'current_rating': rating,
        **get_common_context()
    }
    return render(request, 'main/reviews.html', context)

def promotion_detail(request, code):
    promotion = get_object_or_404(
        Promotion,
        code=code,
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_until__gte=timezone.now()
    )
    
    context = {
        'promotion': promotion,
        **get_common_context()
    }
    return render(request, 'main/promotion_detail.html', context)

@login_required
def profile_bookings(request, status):
    bookings = request.user.client.booking_set.filter(
        status=status
    ).order_by('-created_at')
    
    context = {
        'bookings': bookings,
        'current_status': status,
        **get_common_context()
    }
    return render(request, 'main/profile_bookings.html', context)

def rooms_by_category(request, category_slug):
    category = get_object_or_404(RoomCategory, slug=category_slug)
    rooms = Room.objects.filter(
        category=category,
        is_active=True
    )
    
    # Фильтрация по датам, если они указаны
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    
    if check_in and check_out:
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
            
            # Получаем занятые номера на указанные даты (только активные бронирования)
            booked_rooms = Booking.objects.filter(
                Q(check_in_date__lte=check_out_date) & 
                Q(check_out_date__gte=check_in_date),
                status='active'
            ).values_list('room_id', flat=True)
            
            # Исключаем занятые номера из списка
            rooms = rooms.exclude(id__in=booked_rooms)
        except ValueError:
            messages.error(request, 'Неверный формат даты')
    
    context = {
        'category': category,
        'rooms': rooms,
        'check_in': check_in,
        'check_out': check_out,
        **get_common_context()
    }
    return render(request, 'main/rooms_by_category.html', context)

def rooms_search(request, capacity, comfort_type):
    rooms = Room.objects.filter(
        capacity__gte=capacity,
        category__comfort_type=comfort_type,
        is_active=True
    )
    
    # Фильтрация по датам, если они указаны
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    
    if check_in and check_out:
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
            
            # Получаем занятые номера на указанные даты (только активные бронирования)
            booked_rooms = Booking.objects.filter(
                Q(check_in_date__lte=check_out_date) & 
                Q(check_out_date__gte=check_in_date),
                status='active'
            ).values_list('room_id', flat=True)
            
            # Исключаем занятые номера из списка
            rooms = rooms.exclude(id__in=booked_rooms)
        except ValueError:
            messages.error(request, 'Неверный формат даты')
    
    context = {
        'rooms': rooms,
        'capacity': capacity,
        'comfort_type': comfort_type,
        'check_in': check_in,
        'check_out': check_out,
        **get_common_context()
    }
    return render(request, 'main/rooms_search.html', context)
