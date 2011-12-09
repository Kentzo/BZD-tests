"""The application's model objects"""
from bzdtests.model.meta import Session, Base
from bzdtests.model import meta
from sqlalchemy import orm
from sqlalchemy import schema, types

def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind=engine)
    Base.metadata.create_all(bind=Session.bind)


class TestSuite(Base):
    __tablename__ = 'TestSuite'

    id = schema.Column(types.Integer, primary_key=True)
    name = schema.Column('name', types.Unicode(1000), nullable=False)
    questions_per_test = schema.Column('questions_per_test', types.Integer, default=0, nullable=False)


class Question(Base):
    __tablename__ = 'Question'

    id = schema.Column(types.Integer, primary_key=True)
    testsuite_id = schema.Column(types.Integer, schema.ForeignKey('TestSuite.id'), nullable=False)
    testsuite = orm.relation(TestSuite, backref=orm.backref('questions', order_by=id))
    name = schema.Column(types.Unicode(1000), nullable=False)


class Answer(Base):
    __tablename__ = 'Answer'

    id = schema.Column(types.Integer, primary_key=True)
    name = schema.Column(types.Unicode(255))
    is_correct = schema.Column(types.Boolean, nullable=False)
    question_id = schema.Column(types.Integer, schema.ForeignKey('Question.id'), nullable=False)
    question = orm.relation(Question, backref=orm.backref('answers', order_by=id))