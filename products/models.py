from django.db import models
from django.contrib.auth import get_user_model


#--------------------------------------------------------------------
# a model for products in DB:
class Product(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='نام محصول')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات محصول')
    price = models.PositiveIntegerField(default=0, verbose_name='قیمت محصول')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name='کاربر')

    def __str__(self):
        return f'{self.name}/{self.price}'

    class Meta:
        verbose_name='محصول'
        verbose_name_plural = 'محصولات'
