from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import SmsDetail, ContactDetail
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.forms import ModelForm
from django.views import generic
from .forms import SmsDetailForm, UserForm, ContactDetailForm
from twilio.rest import Client
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from .kandyservice import *
from django.views.decorators.cache import cache_control
import re
from django.contrib.auth.models import User
from django.conf import settings
# Create your views here.

regex = re.compile(r'\+91')



# Kandy specific
domain_api_key = "your_api_key(required)"
domain_secret = "your_api_secret(required)"
user_id = "your_kandy_userid(required)"
source_phone_number = "source_number(required)"



def counter(request):
    return render(request, 'visitor.html')


def messageview(request):
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    all_messages = SmsDetail.objects.filter(user=request.user)
    return render(request, 'messages.html', {'all_messages': all_messages})


def contactview(request):
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    all_contacts = ContactDetail.objects.filter(user=request.user)
    return render(request, 'contacts.html', {'all_contacts': all_contacts})




def index(request):
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    top_5_sms = SmsDetail.objects.filter(
        user=request.user)[:5]
    last_added = ContactDetail.objects.filter(
        user=request.user)[:5]
    context = {'all_sms': top_5_sms, 'last_added': last_added}
    return render(request, 'index.html', context)



def demo(request):
    return render(request, 'demo.html')


def sendfromcontact(request, pk):
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    message = SmsDetail()
    if request.method == 'POST':
        form = SmsDetailForm(request.POST)
        if form.is_valid:
            if bool(regex.search(request.POST['to'])):
                message.to = request.POST['to']
            else:
                message.to = "+91" + request.POST['to']
            message.message_body = request.POST['message_body']
            message.save()
            all_messages = SmsDetail.objects.filter(
                user=request.user)
            return render(request, 'messages.html', {'all_messages':
                                                     all_messages})
    else:
        contact = get_object_or_404(ContactDetail, pk=pk)
        form = SmsDetailForm(initial={'to': contact.phone_num})
        return render(request, 'sendmessage.html', {'form': form, 'contactinst': contact, 'comingfrom': 'contactsend'})


def sendmessage(request):
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    message = SmsDetail()
    if request.method == 'POST':
        form = SmsDetailForm(request.POST)
        if form.is_valid:
            count = request.user.smscount
            if count == 0:
                return render(request, 'sendmessage.html', {'form': form,
                                                            'error': 'Your trial sms limit reached, please contact admin.'})
            # print(request.POST['to'])
            if bool(regex.search(request.POST['to'])):
                destination_phone_number = request.POST['to']
                print(destination_phone_number)
            else:
                destination_phone_number = "+91" + request.POST['to']
                print("Dest: " + destination_phone_number)
            #destination_phone_number = request.POST['to']
            messagebody = request.POST['message_body']
            messagebody = messagebody + "\nSent By: " + \
                request.user.username + " " + request.user.email
            try:
                sms = SMS(domain_api_key, domain_secret, user_id)
                state = sms.send(source_phone_number,
                                 destination_phone_number, messagebody)
                if not state:
                    return render(request, 'sendmessage.html', {'form': form, 'error': 'Problem with API, Could not send.'})
            except Exception as e:
                print('Error: ' + str(e))
            request.user.smscount = request.user.smscount - 1
            message.to = request.POST['to']
            message.message_body = request.POST['message_body']
            message.user = request.user
            contactfound = ContactDetail.objects.filter(
                phone_num=request.POST['to'])
            print("contact: " + str(contactfound))
            if contactfound:
                message.contact = contactfound[0]
            message.save()
            request.user.save()
            return redirect('smsdetails:message')
            # all_messages = SmsDetail.objects.filter(
            #     user=request.user)
            # return render(request, 'messages.html', {'all_messages':
            # all_messages, 'contactfound': contactfound})
    else:
        form = SmsDetailForm()
    return render(request, 'sendmessage.html', {'form': form})


# def sendmessage(request):
#     all_contacts = ContactDetail.objects.all()
#     context = {'all_contacts': all_contacts, }
#     return render(request, 'sendmessage.html', context)


class MessageDelete(DeleteView):
    model = SmsDetail
    success_url = reverse_lazy('smsdetails:message')


class ContactDelete(DeleteView):
    model = ContactDetail
    success_url = reverse_lazy('smsdetails:contact')


@ensure_csrf_cookie
@csrf_protect
def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('smsdetails:index')
                # top_5_sms = SmsDetail.objects.filter(
                #     user=request.user)[:5]
                # last_added = ContactDetail.objects.filter(
                #     user=request.user)[:5]
                # context = {'all_sms': top_5_sms, 'last_added': last_added}
                # return render(request, 'index.html', context)
            else:
                return render(request, 'login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'login.html', {'error_message': 'User with these credentials not found. '})
    return render(request, 'login.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'login.html', context)


def register(request):
    user = User()
    form = UserForm(request.POST)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        user.username = username
        user.email = email
        dupemail = User.objects.filter(email=email)
        dupname = User.objects.filter(username=username)
        if dupemail:
            context = {
                "error": "Email already exist, Please use unique email address",
            }
            return render(request, 'register.html', context)
        if dupname:
            context = {
                "error": "Username already exist, Please use unique username.",
            }
            return render(request, 'register.html', context)
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('smsdetails:index')
    context = {
        "form": form,
    }
    return render(request, 'register.html', context)


def addcontact(request):
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    contact = ContactDetail()
    if request.method == 'POST':
        form = ContactDetailForm(request.POST)
        if form.is_valid():
            contact.first_name = request.POST['first_name']
            contact.last_name = request.POST['last_name']
            contact.phone_num = request.POST['phone_num']
            contact.email = request.POST.get('email', None)
            contact.user = request.user
            contact.save()
            return redirect('smsdetails:contact')
            # all_contacts = ContactDetail.objects.filter(
            #     user=request.user)
            # return render(request, 'contacts.html', {'all_contacts':
            #                                          all_contacts})
    else:
        form = ContactDetailForm()
    return render(request, 'addcontact.html', {'form': form})
