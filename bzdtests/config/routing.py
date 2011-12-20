"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from routes import Mapper

def make_map(config):
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.minimization = False
    map.explicit = False

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')

    # CUSTOM ROUTES HERE
    map.connect('/admin', controller='tests', action='index')
    map.connect('/admin/', controller='tests', action='index')
    map.connect('/admin/account/login', controller='account', action='login')
    map.connect('/admin/account/login/', controller='account', action='login')
    map.connect('/admin/account/change_password', controller='account', action='change_password')
    map.connect('/admin/account/change_password/', controller='account', action='change_password')
    map.connect('/admin/account/set_password', controller='account', action='set_password')
    map.connect('/admin/account/set_password/', controller='account', action='set_password')
    map.connect('/admin/tests', controller='tests', action='index')
    map.connect('/admin/tests/', controller='tests', action='index')
    map.connect('/admin/tests/remove', controller='tests', action='remove_test')
    map.connect('/admin/tests/add', controller='tests', action='add_test')
    map.connect('/admin/tests/{id}', controller='tests', action='edit_test')
    map.connect('/admin/tests/{id}/', controller='tests', action='edit_test')
    map.connect('/admin/tests/{id}/questions', controller='tests', action='edit_test')
    map.connect('/admin/tests/{id}/questions/', controller='tests', action='edit_test')
    map.connect('/admin/tests/{testsuite_id}/questions/{id}', controller='tests', action='edit_question')
    map.connect('/admin/tests/{testsuite_id}/questions/{id}/', controller='tests', action='edit_question')
    map.connect('/admin/tests/{testsuite_id}/questions/{id}/{action}', controller='tests')
    map.connect('/admin/tests/{id}/{action}', controller='tests')
    map.connect('/admin/results', controller='results', action='index')
    map.connect('/admin/results/', controller='results', action='index')
    map.connect('/admin/results/{id}', controller='results', action='show')
    map.connect('/admin/results/{id}/', controller='results', action='show')

    map.connect('', controller='attempt', action='index')
    map.connect('/', controller='attempt', action='index')
    map.connect('/attempt', controller='attempt', action='index')
    map.connect('/attempt/', controller='attempt', action='index')
    map.connect('/attempt/new', controller='attempt', action='new')
    map.connect('/attempt/new/', controller='attempt', action='new')
    map.connect('/attempt/{id}', controller='attempt', action='test')
    map.connect('/attempt/{id}/', controller='attempt', action='test')
    map.connect('/attempt/{id}/check', controller='attempt', action='check')
    map.connect('/attempt/{id}/check/', controller='attempt', action='check')

    map.connect('/{controller}/{action}')
#    map.connect('/{controller}/{action}/{id}')

    return map
