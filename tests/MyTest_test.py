import unittest
from app import App

class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.application = App.createApp()
        self.app = self.application.test_client()
        self.app.testing = True
    
    def test_someTest(self):
        self.assertTrue(True)