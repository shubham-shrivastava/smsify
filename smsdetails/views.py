from django.shortcuts import render
from .models import SmsDetail, ContactDetail
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.forms import ModelForm
from django.views import generic
from .forms import SmsDetailForm
from twilio.rest import Client
from django.shortcuts import get_object_or_404
# Create your views here.


account_sid = "ACc70d30c48ffa3987940f81f3c1bff2a9"
# Your Auth Token from twilio.com/console
auth_token = "ce34579e8f7e2d6e7b7d654356be098a"

client = Client(account_sid, auth_token)


class MessageIndexView(generic.ListView):
    template_name = 'messages.html'
    context_object_name = "all_messages"

    def get_queryset(self):
        return SmsDetail.objects.all()


class ContactIndexView(generic.ListView):
    template_name = 'contacts.html'
    context_object_name = "all_contacts"

    def get_queryset(self):
        return ContactDetail.objects.all()


def index(request):
    top_5_sms = SmsDetail.objects.all()[:5]
    last_added = ContactDetail.objects.all()[:5]
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
    message = SmsDetail()
    if request.method == 'POST':
        form = SmsDetailForm(request.POST)
        if form.is_valid:
            message.to = request.POST['to']
            message.message_body = request.POST['message_body']
            message.save()
            all_messages = SmsDetail.objects.all()
            return render(request, 'messages.html', {'all_messages':
                                                     all_messages})
    else:
        contact = get_object_or_404(ContactDetail, pk=pk)
        form = SmsDetailForm(initial={'to': contact.phone_num})
        return render(request, 'sendmessage.html', {'form': form, 'contactinst': contact, 'comingfrom': 'contactsend'})


def sendmessage(request):
    message = SmsDetail()
    if request.method == 'POST':
        form = SmsDetailForm(request.POST)
        if form.is_valid:
            # messageSent = client.messages.create(
            #     to=str(request.POST['to']),
            #     from_="+14158422848",
            #     body=str(request.POST['message_body']))
            message.to = request.POST['to']
            message.message_body = request.POST['message_body']
            message.save()
            all_messages = SmsDetail.objects.all()
            return render(request, 'messages.html', {'all_messages':
                                                     all_messages})
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
