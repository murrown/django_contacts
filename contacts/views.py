from django.shortcuts import render
from django.http import (
    JsonResponse,
    HttpResponseBadRequest, HttpResponseNotFound, HttpResponseForbidden)
from django.contrib.auth import authenticate
from contacts.models import Contact
import json
from base64 import b64decode


def require_authentication(fn):
    def authenticator(request, *args):
        try:
            method, encoded = request.META['HTTP_AUTHORIZATION'].split()
            assert method.lower() == 'basic'
            username, password = b64decode(encoded).decode().split(':')
            request.user = authenticate(username=username, password=password)
            assert request.user.is_authenticated
        except:
            return HttpResponseForbidden()
        return fn(request, *args)

    return authenticator


@require_authentication
def create_contact(request):
    c = Contact.objects.create(**json.loads(request.body))
    return JsonResponse(c.json)


def query_contacts(request):
    if request.body:
        cs = Contact.objects.filter(**json.loads(request.body))
    else:
        cs = Contact.objects.all()
    return JsonResponse([c.json for c in cs], safe=False)


def get_contact(request, pk):
    c = Contact.objects.get(pk=pk)
    return JsonResponse(c.json)


@require_authentication
def update_contact(request, pk):
    cs = Contact.objects.filter(pk=pk)
    if cs.count() != 1:
        raise Contact.DoesNotExist
    cs.update(**json.loads(request.body))
    return JsonResponse(cs[0].json)


@require_authentication
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
