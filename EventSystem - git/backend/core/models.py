from django.db import models

class SystemSetting(models.Model):
    # تنظیمات عمومی
    site_title = models.CharField(max_length=100, default="رویداد پرو", verbose_name="عنوان سایت")
    support_phone = models.CharField(max_length=20, default="021-00000000", verbose_name="تلفن پشتیبانی")
    logo = models.ImageField(upload_to='site_logo/', null=True, blank=True, verbose_name="لوگو سایت")
    
    # تنظیمات مالی (طبق عکس تنظیمات)
    zarinpal_merchant_id = models.CharField(max_length=100, blank=True, verbose_name="مرچنت کد زرین‌پال")
    
    # تنظیمات پیامک (طبق عکس تنظیمات)
    kavehnegar_api_key = models.CharField(max_length=200, blank=True, verbose_name="کلید API کاوه نگار")
    kavehnegar_sender = models.CharField(max_length=20, default="10002000", verbose_name="شماره فرستنده پیامک")

    class Meta:
        verbose_name = "تنظیمات سیستم"
        verbose_name_plural = "تنظیمات سیستم"

    def __str__(self):
        return self.site_title

    # این تابع باعث میشه فقط یک ردیف تنظیمات داشته باشیم (نه بیشتر)
    def save(self, *args, **kwargs):
        if not self.pk and SystemSetting.objects.exists():
            return
        return super(SystemSetting, self).save(*args, **kwargs)