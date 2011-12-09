from bzdtests.tests import *

class TestEditTestsController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='edit_tests', action='index'))
        # Test response...
