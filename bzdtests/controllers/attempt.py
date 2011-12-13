# -*- coding: utf-8 -*-
import json
import logging
import datetime
from datetime import timedelta, datetime
import re
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
        c.message = request.params.get('message')
        if not hasattr(c, 'message'):
            c.message = u""
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
            if len(first_name) and len(middle_name) and len(last_name) and len(group):
                attempt = Session.query(Attempt).filter((Attempt.first_name==first_name) &
                                                        (Attempt.middle_name==middle_name) &
                                                        (Attempt.last_name==last_name) &
                                                        (Attempt.group==group) &
                                                        (Attempt.testsuite_id==testsuite_id)).order_by(desc(Attempt.date)).first()
                attempt_delay = timedelta(seconds=int(config['attempt_delay']))
                delta = attempt_delay
                if attempt:
                    delta = datetime.now() - attempt.date
                if attempt is None or delta >= attempt_delay:
                    questions_q = Session.query(Question).filter(Question.testsuite_id==testsuite.id).order_by(random()).limit(testsuite.questions_per_test)
                    question_encoder = QuestionEncoder()
                    test_dict = {'name': testsuite.name,
                                 'questions': {question.id: question_encoder.default(question) for question in questions_q}}
                    test =  json.dumps(test_dict)
                    new_attempt = Attempt(first_name=first_name,
                                          middle_name=middle_name,
                                          last_name=last_name,
                                          group=group,
                                          testsuite_id=testsuite.id,
                                          test=test)
                    Session.add(new_attempt)
                    Session.commit()
                    c.attempt_id = new_attempt.id
                    c.test = test_dict
                    return render('/attempt/test.html')
                elif not attempt.is_attempted:
                    c.attempt_id = attempt.id
                    c.test = json.loads(attempt.test)
                    return render('/attempt/test.html')
                else:
                    if attempt.is_attempted_correct:
                        message = u"Вы уже успешно прошли этот тест"
                    else:
                        before_repeat = attempt_delay - delta
                        before_repeat = timedelta(days=before_repeat.days, seconds=before_repeat.seconds)
                        message = u"Вы сможете повтороно пройти тест через " + unicode(before_repeat)
                    redirect(url(controller='attempt', action='index', message=message))
            else:
                redirect(url(controller='attempt', action='index'))
        else:
            redirect(url(controller='attempt', action='index'))

    def check(self, id):
        def number_of_correct_answers(question):
            num = 0
            for answer_id in question['answers']:
                if question['answers'][answer_id]['is_correct']:
                    num += 1
            return num

        attempt = Session.query(Attempt).get(int(id))
        if attempt and not attempt.is_attempted:
            test = json.loads(attempt.test)
            total_num = 0
            for question_id in test['questions']:
                total_num += number_of_correct_answers(test['questions'][question_id])

            prog = re.compile(r'^(\d+)_(\d+)$')
            num = 0
            for param in request.params:
                groups = prog.match(param).groups()
                if len(groups) == 2:
                    question_id = int(groups[0])
                    answer_id = int(groups[1])
                    answer = test['questions'][unicode(question_id)]['answers'][unicode(answer_id)]
                    if answer['is_correct']:
                        num += 1

            attempt.date = datetime.now()
            attempt.is_attempted = True
            attempt.is_attempted_correct = (num == total_num)
            Session.commit()

        if attempt.is_attempted_correct:
            message = u"Вы уже успешно прошли этот тест."
        else:
            message = u"Вам не удалось пройти тест. Количество ошибок: " + unicode(total_num - num)
        redirect(url(controller='attempt', action='index', message=message))