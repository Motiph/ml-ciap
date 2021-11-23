from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from django.utils import timezone

# Create your models here.
class AcmeWebhookMessage(models.Model):
    received_at = models.DateTimeField(help_text="When we received the event.")
    payload = models.JSONField(default=None, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["received_at"]),
        ]

#Reciver to create token to user
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class UserMercadoLibre(models.Model):
    client_id = models.CharField(max_length=50)
    client_secret = models.CharField(max_length=50)
    redirect_uri = models.URLField()

    def save(self, *args, **kwargs):
        if not self.pk and UserMercadoLibre.objects.exists():
            raise ValidationError("Ya existe un registro de este tipo")
        else:
            return super(UserMercadoLibre,self).save(*args, **kwargs)

def GetUserML():
    return UserMercadoLibre.objects.all().first()

class TokenMercadoLibre(models.Model):
    access_token = models.CharField(max_length=200)
    token_type = models.CharField(max_length=100)
    expires_in = models.CharField(max_length=50)
    scope = models.CharField(max_length=50)
    user_id = models.CharField(max_length=50)
    refresh_token = models.CharField(max_length=100)
    received_at = models.DateTimeField(help_text="When we received the event.")

    def save(self, *args, **kwargs):
        if not self.pk and TokenMercadoLibre.objects.exists():
            raise ValidationError("Ya existe un registro de este tipo")
        else:
            return super(TokenMercadoLibre,self).save(*args, **kwargs)

def GetTokenML():
    return TokenMercadoLibre.objects.all().first()

class OrderItemsMercadoLibre(models.Model):
    pack_id_mercadolibre = models.CharField(max_length=70)
    sending = models.BooleanField(default=False)
    received_at = models.DateTimeField(help_text="When we received the event.")

class ItemSellMercadoLibre(models.Model):
    item_id_mercadolibre = models.CharField(max_length=300)
    item_name_mercadolibre = models.CharField(max_length=300)
    item_quatity = models.IntegerField()
    item_price = models.DecimalField(max_digits=9, decimal_places=2, default=0.01)
    payment_id = models.CharField(max_length=300)
    received_at = models.DateTimeField(help_text="When we received the event.")
    brand = models.CharField(max_length=200)
    model = models.CharField(max_length=200)
    part_number = models.CharField(max_length=200)
    order_id = models.ForeignKey(OrderItemsMercadoLibre,on_delete=models.CASCADE,blank=True,null=True)

class DocumentItems(models.Model):
    document = models.FileField(upload_to ='uploads/',verbose_name="Documento")
    description = models.CharField(max_length=200, blank=True, null=True,verbose_name="Descripción")
    created_at = models.DateTimeField(verbose_name="Creado en")
    updated_at = models.DateTimeField(verbose_name="Actualizado en")

    def __str__(self):
        return str(self.created_at)
    class Meta:
        verbose_name = 'Documento subido'
        verbose_name_plural = 'Documentos subidos'

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = timezone.now()
            self.updated_at = timezone.now()
            return super(DocumentItems,self).save(*args, **kwargs)
        else:
            self.updated_at = timezone.now()
            return super(DocumentItems,self).save(*args, **kwargs)