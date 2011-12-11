# -*- coding: utf-8 -*-
import json
import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.templating import render_mako as render

from bzdtests.lib.base import BaseController
from bzdtests.lib import helpers as h
from bzdtests.model import Question, TestSuite, QuestionEncoder
from bzdtests.model.meta import Session

log = logging.getLogger(__name__)

class TestsController(BaseController):

    def index(self):
        c.tests = Session.query(TestSuite).all()
        c.max_name_length = 50
        return render('/test/index.html')

    def add_test(self):
        name = h.escape(request.params.get('name').strip())
        if len(name):
            testsuite = TestSuite(name=name)
            Session.add(testsuite)
            Session.commit()
        redirect(url(controller='tests', action='index'))

    def remove_test(self):
        id = h.escape(request.params.get('id'))
        testsuite = Session.query(TestSuite).get(int(id))
        if testsuite:
            Session.delete(testsuite)
            Session.commit()
        redirect(url(controller='tests', action='index'))

    def edit(self, id):
        testsuite = Session.query(TestSuite).get(int(id))
        if testsuite:
            c.questions = testsuite.questions
            c.max_name_length = 50
            c.testsuite = testsuite
            return render('/test/edit.html')
        else:
            redirect(url(controller='tests', action='index'))

    def set_name(self):
        new_name = h.escape(request.params.get('name').strip())
        if len(new_name):
            id = h.escape(request.params.get('id'))
            testsuite = Session.query(TestSuite).get(int(id))
            if testsuite:
                testsuite.name = new_name
                Session.commit()
                redirect(url(controller='tests', action='edit', id=testsuite.id))
            else:
                redirect(url(controller='tests', action='index'))
        else:
            redirect(url(controller='tests', action='index'))

    def set_questions_per_test(self):
        new_number = h.escape(request.params.get('number').strip())
        if len(new_number):
            id = h.escape(request.params.get('id'))
            testsuite = Session.query(TestSuite).get(int(id))
            if testsuite:
                testsuite.questions_per_test = new_number
                Session.commit()
                redirect(url(controller='tests', action='edit', id=testsuite.id))
            else:
                redirect(url(controller='tests', action='index'))
        else:
            redirect(url(controller='tests', action='index'))

    def add_question(self, id):
        testsuite = Session.query(TestSuite).get(int(id))
        if testsuite:
            name = h.escape(request.params.get('name').strip())
            if len(name):
                question = Question(name=name, testsuite_id=id)
                Session.add(question)
                Session.commit()
            redirect(url(controller='tests', action='edit', id=id))
        else:

            redirect(url(controller='tests', action='index'))

    def remove_question(self, id):
        question_id = h.escape(request.params.get('id'))
        question = Session.query(Question).get(int(question_id))
        testsuite = Session.query(TestSuite).get(int(id))
        if question and testsuite:
            Session.delete(question)
            Session.commit()
            redirect(url(controller='tests', action='edit', id=testsuite.id))
        else:
            redirect(url(controller='tests', action='index'))

    def attempt(self, id):
        testsuite = Session.query(TestSuite).get(int(id))
        question_encoder = QuestionEncoder()
        attempt = {'name': testsuite.name,
                   'answers': [question_encoder.default(question) for question in testsuite.attempt_questions_query()]}
        return json.dumps(attempt)
