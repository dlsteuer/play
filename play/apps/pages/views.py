import codecs
import os

import markdown

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from util import slack


def _serve_md_page(request, md_file, status=200):
    filename = os.path.join(settings.BASE_DIR, "apps", "pages", "md", md_file)
    text = codecs.open(filename, "r", encoding="utf-8").read()
    html = markdown.markdown(text)
    return render(request, "pages/md.html", status=status, context={"html": html})


def about(request):
    return _serve_md_page(request, "404.md")


def conduct(request):
    return render(request, "pages/conduct.html")


def diversity(request):
    return render(request, "pages/diversity.html")


def faq(request):
    return render(request, "pages/faq.html")


def error400(request, exception=None):
    return _serve_md_page(request, "400.md", status=400)


def error403(request, exception=None):
    return _serve_md_page(request, "403.md", status=403)


def error404(request, exception=None):
    return _serve_md_page(request, "404.md", status=404)


def error500(request):
    return _serve_md_page(request, "500.md", status=500)


def help(request):
    return render(request, "pages/help.html")


def learn(request):
    return render(request, "pages/learn.html")


def mission(request):
    return render(request, "pages/mission.html")


def privacy(request):
    return _serve_md_page(request, "privacy.md")


def terms(request):
    return _serve_md_page(request, "terms.md")


@login_required
def report(request):
    report_url = request.POST.get("report_url")
    report_content = request.POST.get("report_content")
    report_content = f"url: {report_url}\n{report_content}"

    slack.log_event(
        user=request.user.id if not request.user.is_anonymous else "anonymous",
        title="Abuse Report",
        message=report_content,
        color="#FF0000",
        fallback=report_content,
    )
    messages.add_message(
        request,
        messages.INFO,
        "Your report has been logged. Our team will review this shortly.",
    )
    return redirect(report_url)
