import json
from django.http import HttpResponseBadRequest, HttpResponse


def json_error(msg):
    return HttpResponseBadRequest('{"status": "error", "reason": "%s"}' % msg,
                                  content_type="application/json")


def json_ok(msg):
    return HttpResponse('{"status": "ok", "reason": "%s"}' % msg,
                        content_type="application/json")


def json_warning(msg):
    return HttpResponse('{"status": "warning", "reason": "%s"}' % msg,
                        content_type="application/json")


def json_response(msg_dict):
    return HttpResponse(json.dumps(msg_dict), content_type="application/json")