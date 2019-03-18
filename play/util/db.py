from django.db import connections
from django.db.utils import OperationalError


def check_connection():
    for name in connections:
        with connections[name].cursor() as cursor:
            cursor.execute("SELECT 1;")
            row = cursor.fetchone()
            if row is None:
                raise OperationalError("Invalid response")
