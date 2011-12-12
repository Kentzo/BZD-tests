"""Setup the BZDTests application"""
import logging

import pylons.test

from bzdtests.config.environment import load_environment
from bzdtests.model import Group, Permission, User
from bzdtests.model.meta import Session, Base

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup bzdtests here"""
    # Don't reload the app if it was loaded under the testing environment
    if not pylons.test.pylonsapp:
        load_environment(conf.global_conf, conf.local_conf)

    # Create the tables if they don't already exist
    Base.metadata.create_all(bind=Session.bind)

    log.info("Adding initial users, groups and permissions...")
    g = Group()
    g.name = u'admin'
    Session.add(g)

    p = Permission()
    p.name = u'admin'
    p.groups.append(g)
    Session.add(p)

    u = User()
    u.username = u'admin'
    u.fullname = u'admin'
    u._set_password('admin')
    u.email = u'admin@example.com'
    u.groups.append(g)
    Session.add(u)

    Session.commit()
