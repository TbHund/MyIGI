from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    
    # Новости с регулярными выражениями
    re_path(r'^news/$', views.news_list, name='news'),
    re_path(r'^news/(?P<pk>\d+)/$', views.news_detail, name='news_detail'),
    re_path(r'^news/archive/(?P<year>\d{4})/(?P<month>\d{2})/$', views.news_archive, name='news_archive'),
    
    path('faq/', views.faq, name='faq'),
    path('contacts/', views.contacts, name='contacts'),
    path('privacy/', views.privacy, name='privacy'),
    
    # Вакансии с регулярными выражениями
    re_path(r'^vacancies/$', views.vacancies, name='vacancies'),
    re_path(r'^vacancies/(?P<category>[\w-]+)/$', views.vacancies_by_category, name='vacancies_by_category'),
    
    # Отзывы с регулярными выражениями
    re_path(r'^reviews/$', views.reviews, name='reviews'),
    re_path(r'^reviews/add/$', views.add_review, name='add_review'),
    re_path(r'^reviews/(?P<rating>[1-5])/$', views.reviews_by_rating, name='reviews_by_rating'),
    
    # Акции с регулярными выражениями
    re_path(r'^promotions/$', views.promotions, name='promotions'),
    re_path(r'^promotions/(?P<code>[\w-]+)/$', views.promotion_detail, name='promotion_detail'),
    
    # Профиль и авторизация
    path('profile/', views.profile, name='profile'),
    re_path(r'^profile/bookings/(?P<status>active|completed|cancelled)/$', views.profile_bookings, name='profile_bookings'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    #Бронирование с   регулярными выражениями
    re_path(r'^book/(?P<room_id>\d+)/$', views.book_room, name='book_room'),
    
    # Маршруты для сотрудников
    path('staff/bookings/', views.staff_bookings, name='staff_bookings'),
    path('staff/clients/', views.staff_clients, name='staff_clients'),
    path('staff/analytics/', views.staff_analytics, name='staff_analytics'),
    #path('staff/booking/<int:booking_id>/', views.staff_booking_detail, name='staff_booking_detail'),
    #path('staff/client/<int:client_id>/', views.staff_client_detail, name='staff_client_detail'),
    
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    #path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
] 