import logging
from django.http import HttpResponse
from util import db

logger = logging.getLogger(__name__)


def alive(request):
    return HttpResponse("ok\n")


def ready(request):
    try:
        db.check_connection()
        return HttpResponse("ok\n")
    except Exception:
        logger.exception("healthz readiness failed")
        return HttpResponse("db: error\n")
