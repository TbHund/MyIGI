from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import (
    News, FAQ, Contact, Vacancy, Review, 
    Promotion, CompanyInfo, Room, RoomCategory
)
from .api_utils import get_random_dog, get_random_cat_fact

def get_common_context():
    """Get common context data for all pages"""
    return {
        'random_dog': get_random_dog(),
        'cat_fact': get_random_cat_fact()
    }

def home(request):
    latest_news = News.objects.filter(is_published=True).order_by('-created_at').first()
    context = {
        'latest_news': latest_news,
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
        # Здесь будет логика регистрации
        pass
    return render(request, 'main/register.html', get_common_context())

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    return render(request, 'main/login.html', get_common_context())

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')
