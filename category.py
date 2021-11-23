import requests
import json

attributesarray = []
category_id = ""
firstcategory = True
category_string= "Accesorios para Vehículos > Refacciones Autos y Camionetas > Suspensión y Dirección > Amortiguadores"
stringcategories = category_string.split(' > ')
attributes = {
    "Posición":"TRASERO",
    "Lado":"Izquierdo/Derecho",
    "OEM":"na",
    }

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

print(category_id)
attributesresponse = requests.get('https://api.mercadolibre.com/categories/'+category_id+'/attributes')
attributesresponsejson = attributesresponse.json()

for id,attribute in attributes.items():
    for atribbuteml in attributesresponsejson:
        if id == atribbuteml['name']:
            if atribbuteml.get('values'):
                for values in atribbuteml.get('values'):
                    if values['name'] == attribute:
                        attributesarray.append({'id':atribbuteml['id'],'value_name':values['id']})
                        break
            else:
                attributesarray.append({'id':atribbuteml['id'],'value_name':attribute})
            break
print(attributesarray)