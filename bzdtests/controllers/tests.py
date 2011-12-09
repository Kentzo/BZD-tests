# -*- coding: utf-8 -*-
import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.templating import render_mako as render
import bzdtests.lib.helpers as h

from bzdtests.lib.base import BaseController
from bzdtests.model import Question, TestSuite
from bzdtests.model.meta import Session

log = logging.getLogger(__name__)

class TestsController(BaseController):

    def index(self):
        c.tests = Session.query(TestSuite).all()
        c.max_name_length = 50
        return render('/test/tests.html')

    def add_test(self):
        name = h.escape(request.params.get('name').strip())
        if len(name):
            suite = TestSuite(name=name)
            Session.add(suite)
            Session.commit()
        redirect(url(controller='tests', action='index'))

    def remove_test(self):
        id = h.escape(request.params.get('id'))
        suite = Session.query(TestSuite).get(int(id))
        if suite:
            for question in suite.questions:
                Session.delete(question)
            Session.delete(suite)
            Session.commit()
        redirect(url(controller='tests', action='index'))

    def edit(self, id):
        suite = Session.query(TestSuite).get(int(id))
        if suite:
            c.questions = suite.questions
            c.max_name_length = 50
            c.suite = suite
            return render('/test/edit.html')
        else:
            redirect(url(controller='tests', action='index'))

    def set_name(self):
        new_name = h.escape(request.params.get('name').strip())
        if len(new_name):
            id = h.escape(request.params.get('id'))
            suite = Session.query(TestSuite).get(int(id))
            if suite:
                suite.name = new_name
                Session.commit()
                redirect(url(controller='tests', action='edit', id=suite.id))
            else:
                redirect(url(controller='tests', action='index'))
        else:
            redirect(url(controller='tests', action='index'))

    def set_questions_per_test(self):
        new_number = h.escape(request.params.get('number').strip())
        if len(new_number):
            id = h.escape(request.params.get('id'))
            suite = Session.query(TestSuite).get(int(id))
            if suite:
                suite.questions_per_test = new_number
                Session.commit()
                redirect(url(controller='tests', action='edit', id=suite.id))
            else:
                redirect(url(controller='tests', action='index'))
        else:
            redirect(url(controller='tests', action='index'))

    def add_question(self, id):
        suite = Session.query(TestSuite).get(int(id))
        if suite:
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
        suite = Session.query(TestSuite).get(int(id))
        if question and suite:
            Session.delete(question)
            Session.commit()
            redirect(url(controller='tests', action='edit', id=suite.id))
        else:
            redirect(url(controller='tests', action='index'))
