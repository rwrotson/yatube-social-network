from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_exist_at_desired_locations(self):
        """Проверка доступности адресов /about/."""
        urllist = ['/about/author/', '/about/tech/']
        for url in urllist:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_about_urls_use_correct_templates(self):
        """URL-адреса используют соответствующие шаблоны."""
        templates_url_names = {
            'author.html': '/about/author/',
            'tech.html': '/about/tech/'
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
