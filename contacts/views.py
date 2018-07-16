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
    """
    @return: Datetime object with the current time, set to the UTC timezone.
    """
    return datetime.utcnow().replace(tzinfo=utc)


def require_authentication(fn):
    """
    Function decorator that checks request headers for HTTP Basic
    Authentication info and forces a HTTP 403: Forbidden response if it is
    missing or incorrect.
    """
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
    """
    Handler for API calls of the form POST /api/

    @param request: JSON request with the contact to be created in the body.
    @return: JSON response containing the contact data (if successful).
    """
    parameters = json.loads(request.body.decode())
    if set(parameters) & set(READ_ONLY_FIELDS):
        return HttpResponseBadRequest()
    parameters['created_by'] = request.user
    c = Contact.objects.create(**parameters)
    return JsonResponse(c.data_dict)


def query_contacts(request):
    """
    Handler for API calls of the form GET /api/

    @param request: JSON request with query filter parameters in the body.
    @return: JSON response containing the list of all contacts matching
        the filter parameters.
    """
    if request.body:
        cs = Contact.objects.filter(**json.loads(request.body.decode()))
    else:
        cs = Contact.objects.all()
    return JsonResponse([c.data_dict for c in cs], safe=False)


def get_contact(request, pk):
    """
    Handler for API calls of the form GET /api/<pk>

    @param request: The request for this API call. (unused)
    @param pk: Primary key of the contact to be returned.
    @return: JSON response containing the indicated contact.
    """
    c = Contact.objects.get(pk=pk)
    return JsonResponse(c.data_dict)


@require_authentication
def update_contact(request, pk):
    """
    Handler for API calls of the form PATCH /api/<pk>

    @param request: JSON request containing the updates to be applied.
    @param pk: Primary key of the contact to be updated.
    @return: JSON response containing the updated contact.
    """
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
    """
    Handler for API calls of the form DELETE /api/<pk>

    @param request: The request for this API call. (unused)
    @param pk: Primary key of the contact to be deleted.
    @return: JSON response containing the deleted contact.
    """
    c = Contact.objects.get(pk=pk)
    deleted_json = c.data_dict
    c.delete()
    return JsonResponse(deleted_json)


def call_api_pk(request, pk):
    """
    Dispatcher for API calls to the /api/<pk> URI. This includes the
    calls that operate on a single, existing contact (GET, PATCH, DELETE).

    @param request: The request for this API call.
    @param pk: Primary key of the contact to be operated on.
    @return: JSON response containing the contact that was operated on.
    """
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
    """
    Dispatcher for API calls to the /api/ URI. This includes all of the
    calls for which a single primary key is not required, either because
    they involve no contacts or multiple contacts (POST, GET).

    @param request: The request for this API call.
    @return: JSON response containing the relevant contact or contacts.
    """
    try:
        if request.method == 'POST':
            return create_contact(request)
        elif request.method == 'GET':
            return query_contacts(request)
    except:
        pass
    return HttpResponseBadRequest()
