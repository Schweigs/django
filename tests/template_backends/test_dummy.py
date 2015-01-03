# coding: utf-8

from __future__ import unicode_literals

from django.http import HttpRequest
from django.middleware.csrf import CsrfViewMiddleware, get_token
from django.template import TemplateDoesNotExist
from django.template.backends.dummy import TemplateStrings
from django.test import SimpleTestCase


class TemplateStringsTests(SimpleTestCase):

    engine_class = TemplateStrings
    backend_name = 'dummy'
    options = {}

    @classmethod
    def setUpClass(cls):
        params = {
            'DIRS': [],
            'APP_DIRS': True,
            'NAME': cls.backend_name,
            'OPTIONS': cls.options,
        }
        cls.engine = cls.engine_class(params)

    def test_from_string(self):
        template = self.engine.from_string("Hello!\n")
        content = template.render()
        self.assertEqual(content, "Hello!\n")

    def test_get_template(self):
        template = self.engine.get_template('template_backends/hello.html')
        content = template.render({'name': 'world'})
        self.assertEqual(content, "Hello world!\n")

    def test_get_template_non_existing(self):
        with self.assertRaises(TemplateDoesNotExist):
            self.engine.get_template('template_backends/non_existing.html')

    def test_html_escaping(self):
        template = self.engine.get_template('template_backends/hello.html')
        context = {'name': '<script>alert("XSS!");</script>'}
        content = template.render(context)

        self.assertIn('&lt;script&gt;', content)
        self.assertNotIn('<script>', content)

    def test_csrf_token(self):
        request = HttpRequest()
        CsrfViewMiddleware().process_view(request, lambda r: None, (), {})

        template = self.engine.get_template('template_backends/csrf.html')
        content = template.render(request=request)

        expected = (
            '<input type="hidden" name="csrfmiddlewaretoken" '
            'value="{}" />'.format(get_token(request)))

        self.assertHTMLEqual(content, expected)

    def test_no_directory_traversal(self):
        with self.assertRaises(TemplateDoesNotExist):
            self.engine.get_template('../forbidden/template_backends/hello.html')

    def test_non_ascii_characters(self):
        template = self.engine.get_template('template_backends/hello.html')
        content = template.render({'name': 'Jérôme'})
        self.assertEqual(content, "Hello Jérôme!\n")