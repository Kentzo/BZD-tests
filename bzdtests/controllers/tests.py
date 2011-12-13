# -*- coding: utf-8 -*-
import json
import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.templating import render_mako as render
from repoze.what.plugins.pylonshq.protectors import ActionProtector
from repoze.what.predicates import has_permission
from sqlalchemy.sql.expression import asc

from bzdtests.lib.base import BaseController
from bzdtests.lib import helpers as h
from bzdtests.model import Question, TestSuite, Answer
from bzdtests.model.meta import Session

log = logging.getLogger(__name__)

class TestsController(BaseController):

    @ActionProtector(has_permission('admin'))
    def index(self):
        c.tests = Session.query(TestSuite).order_by(asc(TestSuite.id)).all()
        return render('/admin/tests/index.html')

    @ActionProtector(has_permission('admin'))
    def add_test(self):
        name = h.escape(request.params.get('name').strip())
        if len(name):
            testsuite = TestSuite(name=name)
            Session.add(testsuite)
            Session.commit()
        redirect(url(controller='tests', action='index'))

    @ActionProtector(has_permission('admin'))
    def remove_test(self):
        id = int(h.escape(request.params.get('id')))
        testsuite = Session.query(TestSuite).get(id)
        if testsuite:
            Session.delete(testsuite)
            Session.commit()
        redirect(url(controller='tests', action='index'))

    @ActionProtector(has_permission('admin'))
    def edit_test(self, id):
        testsuite = Session.query(TestSuite).get(int(id))
        if testsuite:
            c.questions = testsuite.questions
            c.testsuite = testsuite
            return render('/admin/tests/edit_test.html')
        else:
            redirect(url(controller='tests', action='index'))

    @ActionProtector(has_permission('admin'))
    def set_test_params(self, id):
        new_name = h.escape(request.params.get('name').strip())
        new_number = h.escape(request.params.get('number').strip())
        testsuite = Session.query(TestSuite).get(int(id))
        if testsuite:
            if len(new_name):
                testsuite.name = new_name
            if new_number >= 0:
                testsuite.questions_per_test = new_number
            Session.commit()
            redirect(url(controller='tests', action='edit_test', id=testsuite.id))
        else:
            redirect(url(controller='tests', action='index'))

    @ActionProtector(has_permission('admin'))
    def add_question(self, id):
        testsuite = Session.query(TestSuite).get(int(id))
        if testsuite:
            name = h.escape(request.params.get('name').strip())
            if len(name):
                question = Question(name=name, testsuite_id=id)
                Session.add(question)
                Session.commit()
            redirect(url(controller='tests', action='edit_test', id=id))
        else:

            redirect(url(controller='tests', action='index'))

    @ActionProtector(has_permission('admin'))
    def remove_question(self, id):
        question_id = h.escape(request.params.get('id'))
        question = Session.query(Question).get(int(question_id))
        testsuite = Session.query(TestSuite).get(int(id))
        if question and testsuite:
            Session.delete(question)
            Session.commit()
            redirect(url(controller='tests', action='edit_test', id=testsuite.id))
        else:
            redirect(url(controller='tests', action='index'))

    @ActionProtector(has_permission('admin'))
    def edit_question(self, id, testsuite_id):
        question = Session.query(Question).get(int(id))
        testsuite = Session.query(TestSuite).get(int(testsuite_id))
        if question and testsuite:
            c.max_name_length = 50
            c.question = question
            return render('/admin/tests/edit_question.html')
        elif testsuite:
            redirect(url(controller='tests', action='edit_test', id=testsuite.id))
        else:
            redirect(url(controller='tests', action='index'))

    @ActionProtector(has_permission('admin'))
    def set_question_params(self, id, testsuite_id):
        new_name = h.escape(request.params.get('name').strip())
        question = Session.query(Question).get(int(id))
        testsuite = Session.query(TestSuite).get(int(testsuite_id))
        if question and testsuite and len(new_name):
            question.name = new_name
            Session.commit()
            redirect(url(controller='tests', action='edit_question', id=question.id, testsuite_id=testsuite.id))
        elif testsuite:
            redirect(url(controller='tests', action='edit_test', id=testsuite.id))
        else:
            redirect(url(controller='tests', action='index'))


    @ActionProtector(has_permission('admin'))
    def add_answer(self, id, testsuite_id):
        name = h.escape(request.params.get('name').strip())
        is_correct = bool(h.escape(request.params.get('is_correct')))
        question = Session.query(Question).get(int(id))
        testsuite = Session.query(TestSuite).get(int(testsuite_id))
        if question and testsuite and len(name):
            answer = Answer()
            answer.name = name
            answer.is_correct = is_correct
            answer.question_id = question.id
            Session.add(answer)
            Session.commit()
            redirect(url(controller='tests', action='edit_question', id=question.id, testsuite_id=testsuite.id))
        elif testsuite:
            redirect(url(controller='tests', action='edit_test', id=testsuite.id))
        else:
            redirect(url(controller='tests', action='index'))

    @ActionProtector(has_permission('admin'))
    def remove_answer(self, id, testsuite_id):
        answer_id = h.escape(request.params.get('id'))
        answer = Session.query(Answer).get(int(answer_id))
        question = Session.query(Question).get(int(id))
        testsuite = Session.query(TestSuite).get(int(testsuite_id))
        if answer and question and testsuite:
            Session.delete(answer)
            Session.commit()
            redirect(url(controller='tests', action='edit_question', id=question.id, testsuite_id=testsuite.id))
        elif testsuite:
            redirect(url(controller='tests', action='edit_test', id=testsuite.id))
        else:
            redirect(url(controller='tests', action='index'))

    @ActionProtector(has_permission('admin'))
    def save_answers(self, id, testsuite_id):
        question = Session.query(Question).get(int(id))
        testsuite = Session.query(TestSuite).get(int(testsuite_id))
        if question and testsuite:
            for param in request.params:
                if param.startswith('name'):
                    answer_id = int(param[4:])
                    answer = Session.query(Answer).get(int(answer_id))
                    if answer:
                        new_name = h.escape(request.params.get(param))
                        answer.name = new_name
                elif param.startswith('is_correct'):
                    answer_id = int(param[10:])
                    answer = Session.query(Answer).get(int(answer_id))
                    if answer:
                        new_is_correct = bool(h.escape(request.params.get(param)))
                        answer.is_correct = new_is_correct
            Session.commit()
            redirect(url(controller='tests', action='edit_question', id=question.id, testsuite_id=testsuite.id))
        elif testsuite:
            redirect(url(controller='tests', action='edit_test', id=testsuite.id))
        else:
            redirect(url(controller='tests', action='index'))