from django.conf.urls import url
from . import views

app_name = 'smsdetails'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^contacts/$', views.contactview, name="contact"),
    url(r'^messages/$', views.messageview, name="message"),
    url(r'^sendmessage/$', views.sendmessage, name="sendmessage"),
    url(r'^contact/(?P<pk>[0-9]+)/sendmessage/$',
        views.sendfromcontact, name="sendfromcontact"),
    url(r'^demo/', views.demo, name="demo"),
    url(r'messages/(?P<pk>[0-9]+)/delete/$',
        views.MessageDelete.as_view(), name='message-delete'),
    url(r'contacts/(?P<pk>[0-9]+)/delete/$',
        views.ContactDelete.as_view(), name='contact-delete'),
    url(r'^logout_user/$', views.logout_user, name='logout_user'),
    url(r'^addcontact/', views.addcontact, name="addcontact"),
]
