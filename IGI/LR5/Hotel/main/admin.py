from django.contrib import admin
from .models import (
    RoomCategory, Room, Client, Booking, Review,
    Promotion, CompanyInfo, News, FAQ, Contact, Vacancy
)
from datetime import date

@admin.register(RoomCategory)
class RoomCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_night')
    search_fields = ('name',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('number', 'category', 'capacity', 'is_active')
    list_filter = ('category', 'is_active', 'capacity')
    search_fields = ('number', 'description')

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'user', 'phone_number', 'get_age', 'has_child')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone_number', 'middle_name')
    list_filter = ('has_child', 'user__date_joined')
    readonly_fields = ('get_age',)

    def get_age(self, obj):
        if obj.birth_date:
            today = date.today()
            age = today.year - obj.birth_date.year - ((today.month, today.day) < (obj.birth_date.month, obj.birth_date.day))
            return age
        return 'Не указан'
    get_age.short_description = 'Возраст'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'room', 'check_in_date', 'check_out_date', 'status', 'total_price')
    list_filter = ('status', 'check_in_date', 'check_out_date')
    search_fields = ('client__user__username', 'room__number')
    date_hierarchy = 'check_in_date'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('client', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('client__user__username', 'text')
    date_hierarchy = 'created_at'

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
    list_display = ('title', 'created_at', 'is_published', 'get_short_content')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'
    list_editable = ('is_published',)
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'content', 'image')
        }),
        ('Настройки публикации', {
            'fields': ('is_published', 'created_at')
        }),
    )

    def get_short_content(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    get_short_content.short_description = 'Краткое содержание'

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_at')
    search_fields = ('question', 'answer')
    date_hierarchy = 'created_at'

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'phone_number', 'email')
    search_fields = ('name', 'position', 'phone_number', 'email')

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'salary_from', 'salary_to', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description', 'requirements')
    date_hierarchy = 'created_at'
