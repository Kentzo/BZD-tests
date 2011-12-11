import json
import logging
import datetime
from datetime import timedelta, datetime
from sqlalchemy.sql.expression import desc

from sqlalchemy.sql.functions import random

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.configuration import config

from bzdtests.lib.base import BaseController, render
from bzdtests.lib import helpers as h
from bzdtests.model import TestSuite, Attempt, QuestionEncoder, Question
from bzdtests.model.meta import Session

log = logging.getLogger(__name__)

class AttemptController(BaseController):
    def index(self):
        c.tests = Session.query(TestSuite).all()
        return render('/attempt/index.html')

    def new(self):
        testsuite_id = int(h.escape(request.params.get('testsuite_id')))
        testsuite = Session.query(TestSuite).get(testsuite_id)
        if testsuite:
            first_name = h.escape(request.params.get('first_name'))
            middle_name = h.escape(request.params.get('middle_name'))
            last_name = h.escape(request.params.get('last_name'))
            group = h.escape(request.params.get('group'))
            attempt = Session.query(Attempt).filter(Attempt.first_name.contains(first_name) &
                                                    Attempt.middle_name.contains(middle_name) &
                                                    Attempt.last_name.contains(last_name) &
                                                    Attempt.group.contains(group) &
                                                    Attempt.testsuite_id==testsuite_id).order_by(desc(Attempt.date)).first()
            attempt_delay = timedelta(seconds=int(config['attempt_delay']))
            delta = attempt_delay
            if attempt:
                delta = datetime.now() - attempt.date
            if attempt is None or delta >= attempt_delay:
                questions_q = Session.query(Question).filter(Question.testsuite_id==testsuite.id).order_by(random()).limit(testsuite.questions_per_test)
                question_encoder = QuestionEncoder()
                test =  json.dumps({'name': testsuite.name,
                                    'answers': [question_encoder.default(question) for question in questions_q]})
                new_attempt = Attempt(first_name=first_name,
                                      middle_name=middle_name,
                                      last_name=last_name,
                                      group=group,
                                      testsuite_id=testsuite.id,
                                      test=test)
                Session.add(new_attempt)
                Session.commit()
            else:
                redirect(url(controller='attempt', action='index'))
        else:
            redirect(url(controller='attempt', action='index'))