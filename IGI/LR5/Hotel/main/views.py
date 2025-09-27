from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum
from datetime import datetime, timedelta, date
from decimal import Decimal
import calendar
import pytz
from .models import (
    News, FAQ, Contact, Vacancy, Review, 
    Promotion, CompanyInfo, Room, RoomCategory, Booking, Client, PrivacyPolicy, CompanyPartners
)
from .api_utils import get_random_dog, get_random_cat_fact
from .forms import UserRegistrationForm, LoginForm, BookingForm, ReviewForm, ProfileEditForm
from django.core.exceptions import PermissionDenied
from django.db.models.functions import ExtractYear, Now
from statistics import median
import logging

logger = logging.getLogger('main.booking')

def get_common_context():
    #текущее время в UTC
    utc_now = timezone.now()
    
    #временная зона минска
    minsk_tz = pytz.timezone('Europe/Minsk')
    
    #конверт UTC время в минское
    minsk_time = utc_now.astimezone(minsk_tz)
    
    #календарь
    cal = calendar.TextCalendar(calendar.MONDAY)
    current_calendar = cal.formatmonth(minsk_time.year, minsk_time.month)
    
    #эти переменные используются в хтмл шаблонах
    return {
        'random_dog': get_random_dog(),
        'cat_fact': get_random_cat_fact(),
        'current_time': minsk_time.strftime('%d/%m/%Y %H:%M:%S'),
        'utc_time': utc_now.strftime('%d/%m/%Y %H:%M:%S'),
        'user_timezone': 'Europe/Minsk (UTC+3)',
        'calendar': current_calendar,
    }

def home(request):
    latest_news = News.objects.filter(is_published=True).order_by('-created_at').first()
    rooms = Room.objects.filter(is_active=True)
    categories = RoomCategory.objects.all()
    partners = CompanyPartners.objects.all()
    
    latest_changes = {
        'bookings': Booking.objects.order_by('-updated_at').first(),
        'reviews': Review.objects.order_by('-created_at').first(),
        'news': News.objects.order_by('-created_at').first(),
    }
    
    category = request.GET.get('category')
    if category:
        rooms = rooms.filter(category__slug=category)
    
    # Фильтрация по вместимости
    capacity = request.GET.get('capacity')
    if capacity and capacity.isdigit():
        rooms = rooms.filter(capacity__gte=int(capacity))
    
    # Фильтрация по датам, без нее нельзя забронировать номер
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    
    if check_in and check_out:
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
            
            #занятые номера на указанные даты
            booked_rooms = Booking.objects.filter(
                Q(check_in_date__lte=check_out_date) & 
                Q(check_out_date__gte=check_in_date),
                status='active'
            ).values_list('room_id', flat=True)
            
            #занятые номера из списка выписываем
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
        'latest_changes': latest_changes,
        'partners' : partners,
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

# после кнопки читакть далее
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
    privacy = PrivacyPolicy.objects.first()
    context = {
        'privacy': privacy,
        **get_common_context()
    }
    return render(request, 'main/privacy.html', context)

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

def add_review(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Для добавления отзыва необходимо зарегистрироваться')
        return redirect('register')
        
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.client = request.user.client
            review.save()
            messages.success(request, 'Спасибо за ваш отзыв!')
            return redirect('reviews')
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        **get_common_context()
    }
    return render(request, 'main/add_review.html', context)

def promotions(request):
    # рабочие скидки
    active_promotions = Promotion.objects.filter(
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_until__gte=timezone.now()
    ).order_by('valid_until')
    
    # уже нерабочие скидки
    expired_promotions = Promotion.objects.filter(
        Q(valid_until__lt=timezone.now()) |  # по дате закончились
        Q(is_active=False)  # вручную через админку деактивированны
    ).order_by('-valid_until')  # самая недавне-закончившаяся акция
    
    context = {
        'active_promotions': active_promotions,
        'expired_promotions': expired_promotions,
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
    #все категории номеров
    categories = RoomCategory.objects.all()
    rooms = Room.objects.filter(is_active=True)
    
    #фильтр по датам еслиуказаны
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    
    if check_in and check_out:
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
            
            #занятые номера на указанные даты
            booked_rooms = Booking.objects.filter(
                Q(check_in_date__lte=check_out_date) & 
                Q(check_out_date__gte=check_in_date),
                status='active' 
            ).values_list('room_id', flat=True)
            
            #занятые номера не считаем
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

#супер важно
@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id, is_active=True)
    
    if request.method == 'POST':
            form = BookingForm(request.POST)
            if form.is_valid():
                booking = form.save(commit=False)
                booking.client = request.user.client
                booking.room = room
                
                #стоимость
                days = (booking.check_out_date - booking.check_in_date).days
                total_price = room.price_per_night * Decimal(days)
                
                #скидка по промо
                promotion = form.cleaned_data.get('promotion')
                if promotion:
                    discount = total_price * (promotion.discount_percent / Decimal('100'))
                    total_price -= discount
                    messages.success(
                        request,
                        f'Промокод применен! Скидка: {promotion.discount_percent}%'
                    )
                
                booking.total_price = total_price
                
                #свободен ли номер
                conflicting_bookings = Booking.objects.filter(
                    room=room,
                    status='active',
                    check_in_date__lte=booking.check_out_date,
                    check_out_date__gte=booking.check_in_date
                )
                
                if conflicting_bookings.exists():
                    form.add_error(None, 'Этот номер уже забронирован на выбранные даты')
                else:
                    try:
                        booking.save()
                        messages.success(
                            request,
                            f'Номер успешно забронирован! Итоговая стоимость: {total_price} BYN'
                        )
                        return redirect('profile')
                    except Exception as e:
                        form.add_error(None, f'Ошибка при сохранении бронирования: {str(e)}')

    else:
        form = BookingForm()
    
    return render(request, 'main/book_room.html', {'form': form, 'room': room})

def staff_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'client') or not request.user.client.is_staff:
            raise PermissionDenied("У вас нет прав для доступа к этой странице")
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@staff_required
def staff_bookings(request):
    """Представление для просмотра всех бронирований сотрудниками"""
    if request.method == 'POST' and 'delete_booking' in request.POST:
        booking_id = request.POST.get('delete_booking')
        try:
            booking = Booking.objects.get(id=booking_id)
            booking.delete()
            messages.success(request, 'Бронирование успешно удалено')
        except Booking.DoesNotExist:
            messages.error(request, 'Бронирование не найдено')
        return redirect('staff_bookings')
    
    bookings = Booking.objects.all().order_by('-created_at')
    
    #фильтр по статусу
    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)
    
    #фильтр по датам
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        bookings = bookings.filter(check_in_date__gte=date_from)
    if date_to:
        bookings = bookings.filter(check_out_date__lte=date_to)
    
    context = {
        'bookings': bookings,
        'status_choices': Booking.STATUS_CHOICES,
        'selected_status': status,
        'date_from': date_from,
        'date_to': date_to,
        **get_common_context()
    }
    return render(request, 'main/staff/bookings.html', context)

@login_required
@staff_required
def staff_clients(request):
    """Представление для просмотра всех клиентов сотрудниками"""
    clients = Client.objects.filter(is_staff=False).order_by('user__last_name')
    
    #поиск по фио или телу
    search_query = request.GET.get('search')
    if search_query:
        clients = clients.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(middle_name__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    #фильтр есть ли дети
    has_child = request.GET.get('has_child')
    if has_child:
        clients = clients.filter(has_child=has_child == 'true')
    
    context = {
        'clients': clients,
        'search_query': search_query,
        'has_child': has_child,
        **get_common_context()
    }
    return render(request, 'main/staff/clients.html', context)

@login_required
@staff_required
def staff_analytics(request):
    """Представление для аналитики"""
    #подсчет клиентов с детьми и без
    total_clients = Client.objects.filter(is_staff=False)
    clients_with_children = total_clients.filter(has_child=True).count()
    clients_without_children = total_clients.filter(has_child=False).count()
    
    #СТАТИСТИКА бронирований по номерам
    room_bookings = (
        Booking.objects
        .values('room__number', 'room__category__name')
        .annotate(booking_count=Count('id'))
        .order_by('-booking_count')
    )
    
    # данные для диаграммы номеров отеля
    room_numbers = [f"№{booking['room__number']} ({booking['room__category__name']})" for booking in room_bookings]
    booking_counts = [booking['booking_count'] for booking in room_bookings]

    #сттатистика по возрасту клиентов
    today = date.today()
    clients_with_age = []
    for client in total_clients:
        if client.birth_date:
            age = today.year - client.birth_date.year - ((today.month, today.day) < (client.birth_date.month, client.birth_date.day))
            clients_with_age.append(age)

    avg_age = round(sum(clients_with_age) / len(clients_with_age), 1) if clients_with_age else 0
    median_age = round(median(clients_with_age), 1) if clients_with_age else 0

    #возрастные группы для диаграмм
    age_groups = {
        '18-25': 0, '26-35': 0, '36-45': 0,
        '46-55': 0, '56-65': 0, '65+': 0
    }
    
    for age in clients_with_age:
        if age <= 25:
            age_groups['18-25'] += 1
        elif age <= 35:
            age_groups['26-35'] += 1
        elif age <= 45:
            age_groups['36-45'] += 1
        elif age <= 55:
            age_groups['46-55'] += 1
        elif age <= 65:
            age_groups['56-65'] += 1
        else:
            age_groups['65+'] += 1

    #статистика прибыли по категориям номеров люкс.полулюкс.обычный
    category_revenue = (
        Booking.objects
        .values('room__category__name')
        .annotate(total_revenue=Sum('total_price'))
        .order_by('-total_revenue')
    )

    category_names = [item['room__category__name'] for item in category_revenue]
    category_revenues = [float(item['total_revenue']) for item in category_revenue]
    
    context = {
        'clients_with_children': clients_with_children,
        'clients_without_children': clients_without_children,
        'room_numbers': room_numbers,
        'booking_counts': booking_counts,
        'age_groups': list(age_groups.keys()),
        'age_counts': list(age_groups.values()),
        'avg_age': avg_age,
        'median_age': median_age,
        'category_names': category_names,
        'category_revenues': category_revenues,
        **get_common_context()
    }
    return render(request, 'main/staff/analytics.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user.client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user.client)
    
    context = {
        'form': form,
        **get_common_context()
    }
    return render(request, 'main/edit_profile.html', context)

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, client=request.user.client)
    
    #проверка можно ли отменить бронирование
    if booking.status != 'active':
        messages.error(request, 'Можно отменить только активные бронирования')
        return redirect('profile')
    
    #проверка, не поздно ли для отмены (24 часа до заезда)
    if booking.check_in_date <= timezone.now().date() + timedelta(days=1):
        messages.error(request, 'Бронирование можно отменить не позднее чем за 24 часа до заезда')
        return redirect('profile')
    
    booking.status = 'cancelled'
    booking.save()
    
    messages.success(request, 'Бронирование успешно отменено')
    return redirect('profile')
