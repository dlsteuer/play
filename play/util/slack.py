import requests
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

events_slack_url = settings.SLACK_EVENTS_URL


def format(user, title, message, color, fallback):
    return {
        "attachments": [
            {
                "fallback": fallback,
                "color": color,
                "author_name": user,
                "title": title,
                "text": message,
            }
        ]
    }


def log_event(**kwargs):
    try:
        response = requests.post(events_slack_url, json=format(**kwargs))
        response.raise_for_status()
    except Exception:
        logger.exception("failed to send message to slack")
