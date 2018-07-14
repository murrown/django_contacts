from django.shortcuts import render
from django.http import (
    JsonResponse, HttpResponseBadRequest, HttpResponseNotFound)
from contacts.models import Contact
import json

def create_contact(request):
    c = Contact.objects.create(**json.loads(request.body))
    return JsonResponse(c.json)

def query_contacts(request):
    cs = Contact.objects.filter(**json.loads(request.body))
    return JsonResponse([c.json for c in cs], safe=False)

def get_contact(request, pk):
    c = Contact.objects.get(pk=pk)
    return JsonResponse(c.json)

def update_contact(request, pk):
    cs = Contact.objects.filter(pk=pk)
    if cs.count() != 1:
        raise Contact.DoesNotExist
    cs.update(**json.loads(request.body))
    return JsonResponse(cs[0].json)

def delete_contact(request, pk):
    c = Contact.objects.get(pk=pk)
    deleted_json = c.json
    c.delete()
    return JsonResponse(deleted_json)

def call_api_pk(request, pk):
    try:
        if request.method == 'GET':
            return get_contact(request, pk)
        if request.method == 'PATCH':
            return update_contact(request, pk)
        if request.method == 'DELETE':
            return delete_contact(request, pk)
    except Contact.DoesNotExist:
        return HttpResponseNotFound()
    except:
        pass
    return HttpResponseBadRequest()

def call_api(request):
    try:
        if request.method == 'POST':
            return create_contact(request)
        elif request.method == 'GET':
            return query_contacts(request)
    except:
        pass
    return HttpResponseBadRequest()
