"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core.views import (acme_webhook,AcmeWebhookMessageView,Savetoken,GetInfoFromML,
GetItemsSellFromML,ShowOrders,UpdateItemMercadoLibre,CreateItemMercadoLibre,ShowNewOrders,DocumentUpload)
from django.conf.urls import url

admin.site.site_header = 'Sitio de Administración'
admin.site.index_title = "Administración"
admin.site.site_title = "Mi administrador"

urlpatterns = [
    path('admin/', admin.site.urls),
    path("webhooks/",acme_webhook),
    path('viewnotifications/',AcmeWebhookMessageView.as_view()),
    path('savetoken/',Savetoken.as_view()),
    url(r'getinfo/(?P<pk>\d+)/$', GetInfoFromML.as_view()),
    url(r'getitems/(?P<pk>\d+)/$', GetItemsSellFromML.as_view()),
    path(r'showneworders/',ShowNewOrders.as_view()),
    path(r'showorders/',ShowOrders.as_view()),
    path(r'updateitem/',UpdateItemMercadoLibre.as_view()),
    path(r'createitem',CreateItemMercadoLibre.as_view()),
    path(r'upload/',DocumentUpload.as_view())
    ]

if settings.DEBUG:
    urlpatterns+=  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)