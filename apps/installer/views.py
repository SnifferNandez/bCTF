import logging
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login
from django.views.generic import View
from django.contrib.auth.mixins import UserPassesTestMixin
from apps.accounts.models import Account
from apps.installer.forms import InstallForm
from apps.installer.utils import initialize_keys
from apps.scoreboard.utils import create_key
from config import set_key
from django.core.cache import cache

logger = logging.getLogger(__name__)


class UserIsAnonymousMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_anonymous


class InstallView(UserIsAnonymousMixin, View):
    form_class = InstallForm

    def get(self, request, *args, **kwargs):
        if Account.objects.count() == 0:
            return render(self.request, 'templates/installer/install.html', {'form': self.form_class})
        else:
            return redirect('scoreboard:home')

    def post(self, request, *args, **kwargs):
        if Account.objects.count() == 0:
            form = InstallForm(request.POST)
            if form.is_valid():
                new_admin = Account(
                    username=request.POST['admin_username'],
                    email=request.POST['admin_email'],
                    is_superuser=True,
                    is_staff=True,
                    is_active=True,
                    banned=False,
                )
                new_admin.set_password(request.POST['admin_password'])
                new_admin.save()

                try:
                    initialize_keys()
                    set_key("ctf_name", request.POST['ctf_name'])
                    set_key("installed", True)
                    cache.set("theme", "core")
                except Exception as exception:
                    logger.error('Installation failed: {0}'.format(exception))

                new_admin.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, new_admin)
                return render(request, 'templates/installer/success.html')
        else:
            return HttpResponse(status=403)
