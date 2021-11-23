import datetime as dt
from datetime import timedelta
import json
import requests

from django.db.transaction import atomic, non_atomic_requests
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from rest_framework.views import APIView

from .models import AcmeWebhookMessage,GetUserML,TokenMercadoLibre,GetTokenML,ItemSellMercadoLibre,OrderItemsMercadoLibre,DocumentItems

def changeToken():
    token = GetTokenML()
    user = GetUserML()
    actualdate = timezone.now()+ timedelta(hours=-7)
    tokendate = token.received_at + dt.timedelta(hours=-3)
    if (actualdate > tokendate):
        headers ={
            'accept':'application/json',
            'content-type':'application/x-www-form-urlencoded'
        }
        data ={
            'grant_type':'refresh_token',
            'client_id':user.client_id,
            'client_secret':user.client_secret,
            'refresh_token':token.refresh_token
        }
        url = 'https://api.mercadolibre.com/oauth/token'
        response = requests.post(url, headers=headers,data=json.dumps(data))
        jsonResponse = response.json()
        tokenSave = GetTokenML()
        tokenSave.access_token=jsonResponse['access_token']
        tokenSave.token_type=jsonResponse['token_type']
        tokenSave.expires_in=jsonResponse['expires_in']
        tokenSave.scope=jsonResponse['scope']
        tokenSave.user_id=jsonResponse['user_id']
        tokenSave.refresh_token=jsonResponse['refresh_token']
        tokenSave.received_at=actualdate
        tokenSave.save()

# Create your views here.
@csrf_exempt
@require_POST
@non_atomic_requests
def acme_webhook(request):
    AcmeWebhookMessage.objects.filter(
        received_at__lte=timezone.now() - dt.timedelta(days=5)
    ).delete()
    payload = json.loads(request.body)
    changeToken()
    AcmeWebhookMessage.objects.create(
        received_at=timezone.now(),
        payload=payload,
    )
    process_webhook_payload(payload)
    return HttpResponse("Message received okay.", content_type="text/plain")


@atomic
def process_webhook_payload(payload):
    try:
        tokenSave = GetTokenML()
        headers = {'Authorization': 'Bearer '+tokenSave.access_token}
        if (payload['resource']):
            datasplit = payload['resource'].split('/')
            urlpayments = "https://api.mercadopago.com/v1/payments/"+str(datasplit[2])
            responsepayments = requests.get(urlpayments, headers=headers)
            jsonresponsepayments = responsepayments.json()
            idorders = jsonresponsepayments['order']['id']
            statuspayment = str(jsonresponsepayments['status'])
            if statuspayment == 'approved':
                urlorders = 'https://api.mercadolibre.com/orders/'+str(idorders)
                responserorders  = requests.get(urlorders, headers=headers)
                jsonresponseorders = responserorders.json()
                itemsorders = jsonresponseorders['order_items']
                orderid = None
                packid = jsonresponseorders['pack_id']
                if OrderItemsMercadoLibre.objects.filter(pack_id_mercadolibre=str(packid)).exists():
                    orderid = OrderItemsMercadoLibre.objects.get(pack_id_mercadolibre=str(packid))
                else:
                    orderid = OrderItemsMercadoLibre.objects.create(
                        pack_id_mercadolibre = packid,
                        received_at=timezone.now()
                    )

                items = []
                brand = 'None'
                model = 'None'
                part_number = 'None'
                for item in itemsorders:
                    urlitems = "https://api.mercadolibre.com/items/"+str(item['item']['id'])
                    responseitems = requests.get(urlitems, headers=headers)
                    jsonresponseitems = responseitems.json()
                    for attributes in jsonresponseitems['attributes']:
                        if attributes['id'] == 'BRAND':
                            brand = attributes['value_name']
                        if attributes['id'] == 'MODEL':
                            model = attributes['value_name']
                        if attributes['id'] == 'PART_NUMBER':
                            part_number = attributes['value_name']
                    newitem = {
                        "item_id_mercadolibre":item['item']['id'],
                        "item_name_mercadolibre":item['item']['title'],
                        "item_quatity":item['quantity'],
                        "item_price":item['unit_price'],
                        "payment_id":datasplit[2],
                        "received_at":timezone.now(),
                        "brand":brand,
                        "model":model,
                        "part_number":part_number,
                        "order_id":orderid
                        }
                    items.append(newitem)

                if ItemSellMercadoLibre.objects.filter(payment_id=str(datasplit[2])).exists():
                    print("Ya se registro antes")
                else:
                    for item in items:
                        ItemSellMercadoLibre(**item).save()
            else:
                print("Cambio en el pago")
    except Exception as excep:
        print(excep)

class AcmeWebhookMessageView(APIView):
    def get(self, request,format=None):
        try:
            changeToken()
            data = AcmeWebhookMessage.objects.order_by('-id').values()
            array_messages = []
            for message in data:
                dict_message = {
                    "id":message['id'],
                    #subtract 7 hours using mysql
                    "received_at":message['received_at']+ timedelta(hours=-7),
                    "payload":message['payload']
                    }
                array_messages.append(dict_message)
            return Response(array_messages,status=status.HTTP_200_OK)
        except AcmeWebhookMessage.DoesNotExist:
            return Response(None,status=status.HTTP_400_BAD_REQUEST)


class Savetoken(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request,format=None):
        try:
            user = GetUserML()
            code = request.query_params['code']
            headers = {'accept': 'application/json','content-type': 'application/x-www-form-urlencoded'}
            data = {'grant_type':'authorization_code',
            'client_id':user.client_id,
            'client_secret':user.client_secret,
            'code':code,
            'redirect_uri':user.redirect_uri}
            url = 'https://api.mercadolibre.com/oauth/token'
            response = requests.post(url, headers=headers,data=json.dumps(data))
            jsonResponse = response.json()
            if TokenMercadoLibre.objects.exists():
                tokenSave = GetTokenML()
                tokenSave.access_token=jsonResponse['access_token']
                tokenSave.token_type=jsonResponse['token_type']
                tokenSave.expires_in=jsonResponse['expires_in']
                tokenSave.scope=jsonResponse['scope']
                tokenSave.user_id=jsonResponse['user_id']
                tokenSave.refresh_token=jsonResponse['refresh_token']
                tokenSave.received_at=timezone.now()
                tokenSave.save()
            else:
                tokenSave = TokenMercadoLibre(access_token=jsonResponse['access_token'],
                token_type=jsonResponse['token_type'],
                expires_in=jsonResponse['expires_in'],
                scope=jsonResponse['scope'],
                user_id=jsonResponse['user_id'],
                refresh_token=jsonResponse['refresh_token'],
                received_at=timezone.now())
                tokenSave.save()
            return Response(jsonResponse,status=status.HTTP_200_OK)
        except Exception as excep:
            return Response(excep,status=status.HTTP_400_BAD_REQUEST)


class GetInfoFromML(APIView):
    def get(self, request,pk,format=None):
        try:
            changeToken()
            tokenSave = GetTokenML()
            webhookMessage = AcmeWebhookMessage.objects.get(id=pk)
            headers = {'Authorization': 'Bearer '+tokenSave.access_token}
            data = webhookMessage.payload
            if (data['resource']):
                datasplit = data['resource'].split('/')
                print(datasplit[2])
                url = "https://api.mercadolibre.com"+data['resource']
                response = requests.get(url, headers=headers)
                jsonResponse = response.json()
                return Response(jsonResponse,status=status.HTTP_200_OK)
            else:
                return Response("Invalid message",status=status.HTTP_400_BAD_REQUEST)
        except AcmeWebhookMessage.DoesNotExist:
            return Response("Invalid message",status=status.HTTP_400_BAD_REQUEST)
        except data.NameError:
            return Response("Invalid message",status=status.HTTP_400_BAD_REQUEST)
        except Exception as excep:
            return Response(excep.json(),status=status.HTTP_400_BAD_REQUEST)


class GetItemsSellFromML(APIView):
    def get(self, request,pk,format=None):
        try:
            changeToken()
            tokenSave = GetTokenML()
            webhookMessage = AcmeWebhookMessage.objects.get(id=pk)
            headers = {'Authorization': 'Bearer '+tokenSave.access_token}
            data = webhookMessage.payload
            if (data['resource']):
                datasplit = data['resource'].split('/')
                urlpayments = "https://api.mercadopago.com/v1/payments/"+str(datasplit[2])
                responsepayments = requests.get(urlpayments, headers=headers)
                jsonresponsepayments = responsepayments.json()
                idorders = jsonresponsepayments['order']['id']
                urlorders = 'https://api.mercadolibre.com/orders/'+str(idorders)
                responserorders  = requests.get(urlorders, headers=headers)
                jsonresponseorders = responserorders.json()
                itemsorders = jsonresponseorders['order_items']
                items = []
                brand = 'None'
                model = 'None'
                part_number = 'None'

                for item in itemsorders:
                    urlitems = "https://api.mercadolibre.com/items/"+str(item['item']['id'])
                    responseitems = requests.get(urlitems, headers=headers)
                    jsonresponseitems = responseitems.json()
                    for attributes in jsonresponseitems['attributes']:
                        if attributes['id'] == 'BRAND':
                            brand = attributes['value_name']
                        if attributes['id'] == 'MODEL':
                            model = attributes['value_name']
                        if attributes['id'] == 'PART_NUMBER':
                            part_number = attributes['value_name']
                    newitem = {
                        "item_id_mercadolibre":item['item']['id'],
                        "item_name_mercadolibre":item['item']['title'],
                        "item_quatity":item['quantity'],
                        "item_price":item['unit_price'],
                        "payment_id":datasplit[2],
                        "received_at":timezone.now(),
                        "brand":brand,
                        "model":model,
                        "part_number":part_number

                        }
                    items.append(newitem)

                if ItemSellMercadoLibre.objects.filter(payment_id=str(datasplit[2])).exists():
                    return Response(items,status=status.HTTP_200_OK)
                else:
                    for item in items:
                        ItemSellMercadoLibre(**item).save()
                    return Response(items,status=status.HTTP_200_OK)
        except AcmeWebhookMessage.DoesNotExist:
            return Response("NO ENCONTRADO",status=status.HTTP_400_BAD_REQUEST)
        except data.NameError:
            return Response("ERROR EN DATOS",status=status.HTTP_400_BAD_REQUEST)
        except Exception as excep:
            return Response(excep.json(),status=status.HTTP_400_BAD_REQUEST)

class ShowOrders(APIView):
    def get(self, request,format=None):
        data = {}
        for result in OrderItemsMercadoLibre.objects.all():
            items = ItemSellMercadoLibre.objects.filter(order_id = result.id).values()
            dataorder = {
                'pack_id_mercadolibre':result.pack_id_mercadolibre,
                'sending':result.sending,
                'received_at':result.received_at,
                'items':items
                }
            data[result.id] = dataorder
        return Response(data,status=status.HTTP_200_OK)


class ShowNewOrders(APIView):
    def get(self, request,format=None):
        data = {}
        for result in OrderItemsMercadoLibre.objects.exclude(sending=True):
            items = ItemSellMercadoLibre.objects.filter(order_id = result.id).values()
            dataorder = {
                'pack_id_mercadolibre':result.pack_id_mercadolibre,
                'sending':result.sending,
                'received_at':result.received_at,
                'items':items
                }
            data[result.id] = dataorder
            result.sending = True
            result.save()
        return Response(data,status=status.HTTP_200_OK)

class UpdateItemMercadoLibre(APIView):
    def put(self, request,format=None):
        try:
            changeToken()
            tokenSave = GetTokenML()
            data = {}
            quantity = request.data.get('quantity',None)
            price = request.data.get('price',None)
            if quantity is not None:
                data["available_quantity"]= quantity
            if price is not None:
                data["price"]= price
            item = request.data['item']
            headers = {'Authorization': 'Bearer '+tokenSave.access_token}
            url = 'https://api.mercadolibre.com/items/'+str(item)
            response = requests.put(url, headers=headers,data=json.dumps(data))
            responsejson = response.json()
            if 'id' in responsejson:
                return Response(responsejson,status=status.HTTP_200_OK)
            else:
                return Response(responsejson,status=status.HTTP_400_BAD_REQUEST)
        except Exception as excep:
            return Response(excep.json(),status=status.HTTP_400_BAD_REQUEST)

class CreateItemMercadoLibre(APIView):
    def post (self, request,format=None):
        try:
            changeToken()
            tokenSave = GetTokenML()
            headers = {'Authorization': 'Bearer '+tokenSave.access_token}
            url = 'https://api.mercadolibre.com/items'
            itemsCreated = {}

            for item in request.data.get('items',None):

                title = item['title']
                category_string = item['category']
                price = item['price']
                available_quantity = item['quantity']
                warranty_time = item['warranty']
                warranty_type = item['warranty_type']
                pictures = item['pictures']
                attributes = item['attributes']
                description = item['description']


                jsonpictures = []
                for picture in pictures:
                    jsonpictures.append({'source':picture})

                category_id = ""
                firstcategory = True
                stringcategories = category_string.split(' > ')
                for category in stringcategories:
                    if firstcategory == True:
                        categoryresponse = requests.get('https://api.mercadolibre.com/sites/MLM/categories')
                        categoryresponsejson =categoryresponse.json()
                        for responsecat in categoryresponsejson:
                            if category == responsecat['name']:
                                category_id = responsecat['id']
                                firstcategory = False
                                break
                    else:
                        categoryresponse = requests.get('https://api.mercadolibre.com/categories/'+category_id)
                        categoryresponsejson =categoryresponse.json()
                        for responsecat in categoryresponsejson['children_categories']:
                            if category == responsecat['name']:
                                category_id = responsecat['id']
                                break

                attributesarray = []
                attributesarray.append({'id':"BRAND",'value_name':attributes['Marca']})
                attributesarray.append({'id':"PART_NUMBER",'value_name':attributes['Numero_parte']})
                attributes.pop("Marca")
                attributes.pop("Numero_parte")
                if attributes.get('Modelo'):
                    attributesarray.append({'id':"MODEL",'value_name':attributes['Modelo']})
                    attributes.pop('Modelo')
                if attributes.get('SKU'):
                    attributesarray.append({'id':"SELLER_SKU",'value_name':attributes['SKU']})
                    attributes.pop('SKU')
                attributesresponse = requests.get('https://api.mercadolibre.com/categories/'+category_id+'/attributes')
                attributesresponsejson = attributesresponse.json()
                for id,attribute in attributes.items():
                    for atribbuteml in attributesresponsejson:
                        if id == atribbuteml['name']:
                            attributesarray.append({'id':atribbuteml['id'],'value_name':attribute})



                data = {
                    'title':title,
                    'category_id':category_id,
                    'price':price,
                    'currency_id':"MXN",
                    'available_quantity':available_quantity,
                    'buying_mode':"buy_it_now",
                    'condition':"new",
                    'listing_type_id':"gold_pro",
                    'sale_terms':[
                        {
                            'id':"WARRANTY_TYPE",
                            'value_name':str(warranty_type)
                        },
                        {
                            'id':"WARRANTY_TIME",
                            'value_name':str(warranty_time)
                        }
                    ],
                    'pictures':jsonpictures,
                    'attributes':attributesarray
                }

                response = requests.post(url, headers=headers,data=json.dumps(data))
                responsejson = response.json()

                itemML = responsejson['id']
                jsondescription = {'plain_text':description}
                urldescription = "https://api.mercadolibre.com/items/"+str(itemML)+"/description"
                responsedescription = requests.post(urldescription, headers=headers,data=json.dumps(jsondescription))
                responsedescriptionjson = responsedescription.json()
                responsejson["description"] = responsedescriptionjson
                itemsCreated[responsejson["title"]] = responsejson

            return Response(itemsCreated,status=status.HTTP_200_OK)
        except Exception as excep:
            return Response(excep.json(),status=status.HTTP_400_BAD_REQUEST)

from rest_framework.parsers import FileUploadParser
from rest_framework.exceptions import ParseError


class DocumentUpload(APIView):
    parser_class = (FileUploadParser)
    def put(self, request, format=None):
        print(request.data)
        description = request.data.get('description',None)
        if 'document' not in request.data:
            raise ParseError("Empty content")

        document = request.data['document']

        created_at = timezone.now()
        updated_at = created_at
        data = {
                "document" : document,
                "description":description,
                "created_at" : created_at,
                "updated_at" : updated_at
            }
        DocumentItems(**data).save()
        return Response(status=status.HTTP_201_CREATED)




