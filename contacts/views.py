import json
from base64 import b64decode
from datetime import datetime
from pytz import utc

from django.contrib.auth import authenticate
from django.http import (
    JsonResponse,
    HttpResponseBadRequest, HttpResponseNotFound, HttpResponseForbidden)
from contacts.models import Contact


READ_ONLY_FIELDS = ['created', 'created_by', 'modified', 'modified_by', 'pk']


def utcnow():
    return datetime.utcnow().replace(tzinfo=utc)


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
    parameters = json.loads(request.body.decode())
    if set(parameters) & set(READ_ONLY_FIELDS):
        return HttpResponseBadRequest()
    parameters['created_by'] = request.user
    c = Contact.objects.create(**parameters)
    return JsonResponse(c.data_dict)


def query_contacts(request):
    if request.body:
        cs = Contact.objects.filter(**json.loads(request.body.decode()))
    else:
        cs = Contact.objects.all()
    return JsonResponse([c.data_dict for c in cs], safe=False)


def get_contact(request, pk):
    c = Contact.objects.get(pk=pk)
    return JsonResponse(c.data_dict)


@require_authentication
def update_contact(request, pk):
    cs = Contact.objects.filter(pk=pk)
    if cs.count() != 1:
        raise Contact.DoesNotExist
    parameters = json.loads(request.body.decode())
    if set(parameters) & set(READ_ONLY_FIELDS):
        return HttpResponseBadRequest()
    parameters['modified_by'] = request.user
    parameters['modified'] = utcnow()
    cs.update(**parameters)
    return JsonResponse(cs[0].data_dict)


@require_authentication
def delete_contact(request, pk):
    c = Contact.objects.get(pk=pk)
    deleted_json = c.data_dict
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
