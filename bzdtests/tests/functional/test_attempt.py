from bzdtests.tests import *

class TestAttemptController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='attempt', action='index'))
        # Test response...
