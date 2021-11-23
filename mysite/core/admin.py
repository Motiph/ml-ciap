from django.contrib import admin
from .models import AcmeWebhookMessage,UserMercadoLibre,TokenMercadoLibre,ItemSellMercadoLibre,OrderItemsMercadoLibre,DocumentItems

# Register your models here.
admin.site.register(AcmeWebhookMessage)
admin.site.register(UserMercadoLibre)
admin.site.register(TokenMercadoLibre)
admin.site.register(ItemSellMercadoLibre)
admin.site.register(OrderItemsMercadoLibre)

@admin.register(DocumentItems)
class DocumentItemsAdmin(admin.ModelAdmin):
    list_display = ("created_at","document","description", "updated_at")
    list_filter = ("created_at","updated_at" )
    search_fields = ("document", )
    fields = ("document","description")

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Documentos subidos.'}
        return super(DocumentItemsAdmin, self).changelist_view(request, extra_context=extra_context)
