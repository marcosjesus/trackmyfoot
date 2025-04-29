from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import PDFData, PDFKeyword

User = get_user_model()

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'position', 'is_staff', 'is_active')
    list_filter = ('user_type', 'position', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('username',)
    fieldsets = UserAdmin.fieldsets + (
        ('Informações adicionais', {'fields': ('user_type', 'position')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações adicionais', {'fields': ('user_type', 'position')}),
    )

@admin.register(PDFKeyword)
class PDFKeywordAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'pattern')
    search_fields = ('description',)
    list_per_page = 25

@admin.register(PDFData)
class PDFDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'description', 'value_before', 'value_after', 'date', 'playing_time', 'start_time', 'duration')
    search_fields = ('user__username', 'description')
    list_filter = ('user', 'date')
    list_per_page = 25
