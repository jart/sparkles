
from django.test import TestCase
from django.core.urlresolvers import reverse


class BasicTest(TestCase):
    fixtures = []

    def setUp(self):
        pass

    def test_index(self):
        url = reverse("sparkles.views.index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_notfound(self):
        response = self.client.get("/euhcuehsrcoahucr/")
        self.assertEqual(response.status_code, 404)

    def test_error(self):
        url = reverse("sparkles.views.error")
        self.assertRaises(AssertionError, lambda: self.client.get(url))
