import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from repoze.what.plugins.pylonshq.protectors import ActionProtector
from repoze.what.predicates import has_permission

from bzdtests.lib.base import BaseController, render
from bzdtests.model import User
from bzdtests.model.meta import Session

log = logging.getLogger(__name__)

class AccountController(BaseController):

    def login(self):
        """
        This is where the login form should be rendered.
        Without the login counter, we won't be able to tell if the user has
        tried to log in with wrong credentials
        """
        identity = request.environ.get('repoze.who.identity')
        came_from = str(request.GET.get('came_from', '')) or url(controller='tests', action='index')
        if identity:
            redirect(url(came_from))
        else:
            c.came_from = came_from
            c.login_counter = request.environ['repoze.who.logins'] + 1
            return render('/admin/account/login.html')

    @ActionProtector(has_permission('admin'))
    def change_password(self):
        return render('/admin/account/change_password.html')

    @ActionProtector(has_permission('admin'))
    def set_password(self):
        new_password = request.params.get('new_password')
        repeat_password = request.params.get('repeat_password')
        if new_password == repeat_password:
            identity = request.environ.get('repoze.who.identity')
            user = identity['user']
            if user:
                user._set_password(new_password)
                Session.commit()
            redirect(url(controller='tests', action='index'))
        else:
            redirect(url(controller='account', action='change_password'))