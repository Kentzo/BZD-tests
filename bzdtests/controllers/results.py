import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from repoze.what.plugins.pylonshq.protectors import ActionProtector
from repoze.what.predicates import has_permission
from sqlalchemy.sql.expression import desc

from bzdtests.lib.base import BaseController, render
from bzdtests.model import Attempt
from bzdtests.model.meta import Session

log = logging.getLogger(__name__)

class ResultsController(BaseController):

    @ActionProtector(has_permission('admin'))
    def index(self):
        c.attempts = Session.query(Attempt).order_by(desc(Attempt.date)).all()
        return render('/admin/results/index.html')

    @ActionProtector(has_permission('admin'))
    def show(self, id):
        attempt = Session.query(Attempt).get(int(id))
        if attempt and attempt.is_attempted:
            c.attempt = attempt
            return render('/admin/results/show.html')
        else:
            redirect(url(controller='results', action='index'))