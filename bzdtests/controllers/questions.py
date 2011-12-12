# -*- coding: utf-8 -*-
import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.templating import render_mako as render
import bzdtests.lib.helpers as h

from bzdtests.lib.base import BaseController, render
from bzdtests.model import Question, TestSuite, Answer
from bzdtests.model.meta import Session

log = logging.getLogger(__name__)

class QuestionsController(BaseController):

    def edit(self, id, testsuite_id):
        question = Session.query(Question).get(int(id))
        testsuite = Session.query(TestSuite).get(int(testsuite_id))
        if question and testsuite:
            c.max_name_length = 50
            c.question = question
            return render('/question/edit.html')
        elif testsuite:
            redirect(url(controller='tests', action='edit', id=int(id)))
        else:
            redirect(url(controller='tests', action='index'))

    def set_name(self, id, testsuite_id):
        new_name = h.escape(request.params.get('name').strip())
        question = Session.query(Question).get(int(id))
        testsuite = Session.query(TestSuite).get(int(testsuite_id))
        if question and testsuite and len(new_name):
            question.name = new_name
            Session.commit()
            redirect(url(controller='questions', action='edit', id=question.id, testsuite_id=testsuite.id))
        elif testsuite:
            redirect(url(controller='tests', action='edit', id=testsuite.id))
        else:
            redirect(url(controller='tests', action='index'))

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
            redirect(url(controller='questions', action='edit', id=question.id, testsuite_id=testsuite.id))
        elif testsuite:
            redirect(url(controller='tests', action='edit', id=testsuite.id))
        else:
            redirect(url(controller='tests', action='index'))

    def remove_answer(self, id, testsuite_id):
        answer_id = h.escape(request.params.get('id'))
        answer = Session.query(Answer).get(int(answer_id))
        question = Session.query(Question).get(int(id))
        testsuite = Session.query(TestSuite).get(int(testsuite_id))
        if answer and question and testsuite:
            Session.delete(answer)
            Session.commit()
            redirect(url(controller='questions', action='edit', id=question.id, testsuite_id=testsuite.id))
        elif testsuite:
            redirect(url(controller='tests', action='edit', id=testsuite.id))
        else:
            redirect(url(controller='tests', action='index'))

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
            redirect(url(controller='questions', action='edit', id=question.id, testsuite_id=testsuite.id))
        elif testsuite:
            redirect(url(controller='tests', action='edit', id=testsuite.id))
        else:
            redirect(url(controller='tests', action='index'))
