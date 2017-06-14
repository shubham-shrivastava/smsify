from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'smsdetails'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^contacts/$', views.ContactIndexView.as_view(), name="contact"),
    url(r'^messages/$', views.MessageIndexView.as_view(), name="message"),
    url(r'^sendmessage/$', views.sendmessage, name="sendmessage"),
    url(r'^contact/(?P<pk>[0-9]+)/sendmessage/$',
        views.sendfromcontact, name="sendfromcontact"),
    url(r'^demo/', views.demo, name="demo"),
    url(r'messages/(?P<pk>[0-9]+)/delete/$',
        views.MessageDelete.as_view(), name='message-delete'),
    url(r'contacts/(?P<pk>[0-9]+)/delete/$',
        views.ContactDelete.as_view(), name='contact-delete'),
]
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
