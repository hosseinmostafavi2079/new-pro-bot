from django.contrib import admin
from .models import SystemSetting

@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('site_title', 'support_phone')
    
    # این تابع باعث میشه دکمه "افزودن" رو حذف کنیم اگر قبلا تنظیمات ساخته شده
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)