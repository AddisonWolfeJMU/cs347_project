# api/tests/test_sanity.py
from django.test import TestCase

class Sanity(TestCase):
    def test_runs(self):
        self.assertTrue(True)