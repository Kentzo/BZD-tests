"""The application's model objects"""
import datetime
from sqlalchemy.schema import Index
from bzdtests.model.meta import Session, Base
import json
from sqlalchemy import orm
from sqlalchemy import schema, types

def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind=engine)
    Base.metadata.create_all(bind=Session.bind)


class TestSuite(Base):
    __tablename__ = 'TestSuite'
    __table_args__ = ({'mysql_engine':'InnoDB'}, )

    id = schema.Column(types.Integer, primary_key=True)
    name = schema.Column('name', types.UnicodeText, nullable=False)
    questions_per_test = schema.Column('questions_per_test', types.Integer, default=20, nullable=False)
    questions = orm.relationship('Question', cascade='all, delete-orphan', passive_deletes=True)


class Question(Base):
    __tablename__ = 'Question'
    __table_args__ = ({'mysql_engine':'InnoDB'}, )

    id = schema.Column(types.Integer, primary_key=True)
    testsuite_id = schema.Column(types.Integer, schema.ForeignKey('TestSuite.id', ondelete='CASCADE'), nullable=False)
    testsuite = orm.relationship(TestSuite)
    name = schema.Column(types.UnicodeText, nullable=False)
    answers = orm.relationship('Answer', cascade='all, delete-orphan', passive_deletes=True)


class Answer(Base):
    __tablename__ = 'Answer'
    __table_args__ = ({'mysql_engine':'InnoDB'}, )

    id = schema.Column(types.Integer, primary_key=True)
    name = schema.Column(types.Unicode(255), nullable=False)
    is_correct = schema.Column(types.Boolean, nullable=False)
    question_id = schema.Column(types.Integer, schema.ForeignKey('Question.id', ondelete='CASCADE'), nullable=False)
    question = orm.relationship(Question)


class Attempt(Base):
    __tablename__ = 'Attempt'
    __table_args__ = (Index('name_group_test_date', 'first_name', 'middle_name', 'last_name', 'group', 'testsuite_id', 'date'), {'mysql_engine':'InnoDB'})

    id = schema.Column(types.Integer, primary_key=True)
    first_name = schema.Column(types.Unicode(255), nullable=False)
    middle_name = schema.Column(types.Unicode(255), nullable=False)
    last_name = schema.Column(types.Unicode(255), nullable=False)
    group = schema.Column(types.Unicode(255), nullable=False)
    testsuite_id = schema.Column(types.Integer, schema.ForeignKey('TestSuite.id'), nullable=False)
    testsuite = orm.relationship(TestSuite)
    test = schema.Column(types.Binary, nullable=False)
    date = schema.Column(types.DateTime, default=datetime.datetime.now, nullable=False)
    is_attempted = schema.Column(types.Boolean, default=False, nullable=False)


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