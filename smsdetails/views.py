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
# Create your views here.


account_sid = "ACc70d30c48ffa3987940f81f3c1bff2a9"
# Your Auth Token from twilio.com/console
auth_token = "ce34579e8f7e2d6e7b7d654356be098a"


# Kandy specific
domain_api_key = "DAKb452d7f3dc3647788008c6f27fbf0d40"
domain_secret = "DAS016c34a169e1498f801ef68a7cdab9a1"
user_id = "shubham"
source_phone_number = "+919511727469"

client = Client(account_sid, auth_token)


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


# class MessageIndexView(generic.ListView):
#     template_name = 'messages.html'
#     context_object_name = "all_messages"

#     def get_queryset(self):
#         return SmsDetail.objects.all()


# class ContactIndexView(generic.ListView):
#     template_name = 'contacts.html'
#     context_object_name = "all_contacts"

#     def get_queryset(self):
#         return ContactDetail.objects.all()


def index(request):
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    top_5_sms = SmsDetail.objects.filter(
        user=request.user)[:5]
    last_added = ContactDetail.objects.filter(
        user=request.user)[:5]
    context = {'all_sms': top_5_sms, 'last_added': last_added}
    return render(request, 'index.html', context)


# def contact(request):
#     all_contacts = ContactDetail.objects.all()
#     context = {'all_contacts': all_contacts, }
#     return render(request, 'contacts.html', context)


# def message(request):
#     all_messages = SmsDetail.objects.all()
#     context = {'all_messages': all_messages, }
#     return render(request, 'messages.html', context)

def demo(request):
    return render(request, 'demo.html')


def sendfromcontact(request, pk):
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    message = SmsDetail()
    if request.method == 'POST':
        form = SmsDetailForm(request.POST)
        if form.is_valid:
            message.to = request.POST['to']
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
            destination_phone_number = request.POST['to']
            messagebody = request.POST['message_body']
            try:
                sms = SMS(domain_api_key, domain_secret, user_id)
                sms.send(source_phone_number,
                         destination_phone_number, messagebody)
            except Exception as e:
                print('Error: ' + str(e))
            # messageSent = client.messages.create(
            #     to=str(request.POST['to']),
            #     from_="+14158422848",
            #     body=str(request.POST['message_body']))
            message.to = request.POST['to']
            message.message_body = request.POST['message_body']
            message.user = request.user
            contactfound = ContactDetail.objects.filter(
                phone_num=request.POST['to'])
            print("contact: " + str(contactfound))
            if contactfound:
                message.contact = contactfound[0]
            message.save()
            all_messages = SmsDetail.objects.filter(
                user=request.user)
            return render(request, 'messages.html', {'all_messages':
                                                     all_messages, 'contactfound': contactfound})
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
            return render(request, 'login.html', {'error_message': 'Invalid login'})
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
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
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
            all_contacts = ContactDetail.objects.filter(
                user=request.user)
            return render(request, 'contacts.html', {'all_contacts':
                                                     all_contacts})
    else:
        form = ContactDetailForm()
    return render(request, 'addcontact.html', {'form': form})
