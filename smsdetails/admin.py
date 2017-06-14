from django.contrib import admin
from .models import ContactDetail, SmsDetail
# Register your models here.


@admin.register(ContactDetail)
class ContactDetailAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_num')


@admin.register(SmsDetail)
class SmsDetailAdmin(admin.ModelAdmin):
    list_display = ('contact', 'to', 'message_body')
