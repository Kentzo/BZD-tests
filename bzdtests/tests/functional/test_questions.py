from bzdtests.tests import *

class TestQuestionsController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='questions', action='index'))
        # Test response...
