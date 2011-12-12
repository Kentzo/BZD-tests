from repoze.what.plugins.quickstart import setup_sql_auth
from bzdtests.model import Session
from bzdtests.model import User, Group, Permission

def add_auth(app, config):
    """
    Add authentication and authorization middleware to the ``app``.

    We're going to define post-login and post-logout pages
    to do some cool things.

    """
    # we need to provide repoze.what with translations as described here:
    # http://what.repoze.org/docs/plugins/quickstart/
    return setup_sql_auth(app, User, Group, Permission, Session,
                          login_url='/admin/account/login',
                          post_login_url='/admin',
                          post_logout_url='/',
                          login_handler='/admin/account/login_handler',
                          logout_handler='/admin/account/logout',
                          cookie_secret=config.get('cookie_secret'),
                          translations={
                              'user_name': 'username',
                              'group_name': 'name',
                              'permission_name': 'name',
                              })