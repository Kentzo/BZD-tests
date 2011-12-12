"""The application's model objects"""
import datetime
from beaker.crypto.util import sha1
import os
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
    __table_args__ = (schema.Index('name_group_test_date', 'first_name', 'middle_name', 'last_name', 'group', 'testsuite_id', 'date'), {'mysql_engine':'InnoDB'})

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


# This is the association table for the many-to-many relationship between
# groups and permissions.
group_permission_table = schema.Table('group_permission', Base.metadata,
                                      schema.Column('group_id', types.Integer, schema.ForeignKey('Group.id')),
                                      schema.Column('permission_id', types.Integer, schema.ForeignKey('Permission.id')),
                                      )

# This is the association table for the many-to-many relationship between
# groups and users
user_group_table = schema.Table('user_group', Base.metadata,
                                schema.Column('user_id', types.Integer, schema.ForeignKey('User.id')),
                                schema.Column('group_id', types.Integer, schema.ForeignKey('Group.id')),
                                )


class Group(Base):
    __tablename__ = 'Group'
    __table_args__ = ({'mysql_engine':'InnoDB'}, )

    id = schema.Column(types.Integer, primary_key=True)
    name = schema.Column(types.Unicode(255), unique=True, nullable=False)
    permissions = orm.relationship('Permission', secondary=group_permission_table)
    users = orm.relationship('User', secondary=user_group_table)


class User(Base):
    __tablename__ = 'User'
    __table_args__ = ({'mysql_engine':'InnoDB'}, )

    id = schema.Column(types.Integer, primary_key=True)
    username = schema.Column(types.Unicode(255), unique=True, nullable=False)
    password = schema.Column(types.Unicode(255), unique=True, nullable=False)
    groups = orm.relationship('Group', secondary=user_group_table)

    def _set_password(self, password):
        """Hash password on the fly."""
        if isinstance(password, unicode):
            password_8bit = password.encode('UTF-8')
        else:
            password_8bit = password

        salt = sha1()
        salt.update(os.urandom(60))
        hash = sha1()
        hash.update(password_8bit + salt.hexdigest())
        hashed_password = salt.hexdigest() + hash.hexdigest()

        # Make sure the hased password is an UTF-8 object at the end of the
        # process because SQLAlchemy _wants_ a unicode object for Unicode
        # fields
        if not isinstance(hashed_password, unicode):
            hashed_password = hashed_password.decode('UTF-8')

        self.password = hashed_password

    def _get_password(self):
        """Return the password hashed"""
        return self.password

    def validate_password(self, password):
        """
        Check the password against existing credentials.

        :param password: the password that was provided by the user to
            try and authenticate. This is the clear text version that we will
            need to match against the hashed one in the database.
        :type password: unicode object.
        :return: Whether the password is valid.
        :rtype: bool

        """
        hashed_pass = sha1()
        hashed_pass.update(password + self.password[:40])
        return self.password[40:] == hashed_pass.hexdigest()


class Permission(Base):
    __tablename__ = 'Permission'
    __table_args__ = ({'mysql_engine':'InnoDB'}, )

    id = schema.Column(types.Integer, primary_key=True)
    name = schema.Column(types.Unicode(255), unique=True, nullable=False)
    groups = orm.relationship('Group', secondary=group_permission_table)


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