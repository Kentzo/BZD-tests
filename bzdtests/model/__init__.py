"""The application's model objects"""
from bzdtests.model.meta import Session, Base
import json
from sqlalchemy import orm
from sqlalchemy import schema, types
from sqlalchemy.sql.functions import random

def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind=engine)
    Base.metadata.create_all(bind=Session.bind)


class TestSuite(Base):
    __tablename__ = 'TestSuite'

    id = schema.Column(types.Integer, primary_key=True)
    name = schema.Column('name', types.Unicode(1000), nullable=False)
    questions_per_test = schema.Column('questions_per_test', types.Integer, default=20, nullable=False)
    questions = orm.relationship('Question', cascade='all, delete-orphan', passive_deletes=True)

    def attempt_questions_query(self):
        if self.questions_per_test > 0:
            return Session.query(Question).filter(Question.testsuite_id == self.id).order_by(random()).limit(
                self.questions_per_test)
        else:
            raise RuntimeError('Number of questions per test MUST be greater than 0')


class Question(Base):
    __tablename__ = 'Question'

    id = schema.Column(types.Integer, primary_key=True)
    testsuite_id = schema.Column(types.Integer, schema.ForeignKey('TestSuite.id', ondelete='CASCADE'), nullable=False)
    testsuite = orm.relationship(TestSuite)
    name = schema.Column(types.Unicode(1000), nullable=False)
    answers = orm.relationship('Answer', cascade='all, delete-orphan', passive_deletes=True)


class Answer(Base):
    __tablename__ = 'Answer'

    id = schema.Column(types.Integer, primary_key=True)
    name = schema.Column(types.Unicode(255))
    is_correct = schema.Column(types.Boolean, nullable=False)
    question_id = schema.Column(types.Integer, schema.ForeignKey('Question.id', ondelete='CASCADE'), nullable=False)
    question = orm.relationship(Question)


class TestSuiteEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, TestSuite):
            return {'id': o.id,
                    'name': o.name,
                    'questions_per_test': o.questions_per_test}
        else:
            raise TypeError('Object MUST be an instance of TestSuite')


class QuestionEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Question):
            answer_encoder = AnswerEncoder()
            return {'id': o.id,
                    'name': o.name,
                    'answers': [answer_encoder.default(answer) for answer in o.answers]}
        else:
            raise TypeError('Object MUST be an instance of Question')


class AnswerEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Answer):
            return {'id': o.id,
                    'name': o.name,
                    'is_correct': o.is_correct}
        else:
            raise TypeError('Object must be an instance of Answer')