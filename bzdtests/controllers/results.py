import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from sqlalchemy.sql.expression import desc

from bzdtests.lib.base import BaseController, render
from bzdtests.model import Attempt
from bzdtests.model.meta import Session

log = logging.getLogger(__name__)

class ResultsController(BaseController):

    def index(self):
        c.attempts = Session.query(Attempt).order_by(desc(Attempt.date)).all()
        return render('/admin/results/index.html')

    def show(self, id):
        attempt = Session.query(Attempt).get(int(id))
        if attempt:
            c.attempt = attempt
            return render('/admin/results/show.html')
        else:
            redirect(url(controller='results', action='index'))