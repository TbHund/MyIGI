from django.contrib import admin
from .models import (
    RoomCategory, Room, Client, Booking, Review,
    Promotion, CompanyInfo, News, FAQ, Contact, Vacancy
)
from datetime import date

@admin.register(RoomCategory)
class RoomCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('number', 'category', 'capacity', 'price_per_night', 'is_active')
    list_filter = ('category', 'is_active', 'capacity')
    search_fields = ('number', 'description')

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'phone_number', 'birth_date', 'has_child', 'get_email', 'is_staff')
    list_filter = ('has_child', 'is_staff')
    search_fields = ('user__first_name', 'user__last_name', 'middle_name', 'phone_number')
    list_editable = ('is_staff',)
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'get_client_full_name',
        'room',
        'check_in_date',
        'check_out_date',
        'total_price',
        'status',
        'promotion',
        'created_at'
    )
    list_filter = ('status', 'check_in_date', 'check_out_date')
    search_fields = (
        'client__user__first_name',
        'client__user__last_name',
        'room__number',
        'promotion__code'
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def get_client_full_name(self, obj):
        return obj.client.get_full_name()
    get_client_full_name.short_description = 'Клиент'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('client', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('client__user__first_name', 'client__user__last_name', 'text')

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'valid_from', 'valid_until', 'is_active')
    list_filter = ('is_active', 'discount_percent')
    search_fields = ('code', 'description')
    date_hierarchy = 'valid_from'

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('title', 'updated_at')
    search_fields = ('title', 'content')

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_published')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content')

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_at')
    search_fields = ('question', 'answer')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'phone_number', 'email')
    search_fields = ('name', 'position', 'phone_number', 'email')

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'salary_from', 'salary_to', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description', 'requirements')
