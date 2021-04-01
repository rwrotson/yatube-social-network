from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Group, Post

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser')
        cls.user2 = User.objects.create_user(username='testuser2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testgroup',
            description='Тестовое описание группы'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            pk=100,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(URLTests.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(URLTests.user2)

    def test_url_exists(self):
        """Доступность страниц, доступных любому пользователю."""
        urllist = ['/group/testgroup/', '/',
                   '/testuser/', '/testuser/100/']
        for url in urllist:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_edit_by_guest_user(self):
        """Страница /<username>/<post_id>/edit/ недоступна
        неавторизированному пользователю"""
        response = self.guest_client.get('/testuser/100/edit/')
        self.assertNotEqual(response.status_code, HTTPStatus.OK)

    def test_url_edit_by_other_user(self):
        """Страница /<username>/<post_id>/edit/ недоступна
        авторизированному пользователю не автору поста"""
        response = self.authorized_client2.get('/testuser/100/edit/')
        self.assertNotEqual(response.status_code, HTTPStatus.OK)

    def test_url_edit_by_other_user(self):
        """Страница /<username>/<post_id>/edit/ доступна
        авторизированному автору поста"""
        response = self.authorized_client.get('/testuser/100/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_authorized(self):
        """Страница /new/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/new/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_new_url_redirect_anonymous(self):
        """Страница /new/ перенаправит анонимного пользователя
        на страницу логина."""
        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(response,
                             '/auth/login/?next=/new/')

    def test_edit_url_redirect_anonymous(self):
        """Страница /<username>/<post_id>/edit/ перенаправит
        анонимного пользователя на страницу просмотра поста."""
        response = self.guest_client.get('/testuser/100/edit/',
                                         follow=True)
        self.assertRedirects(response, '/testuser/100/')

    def test_edit_url_redirect_other_user(self):
        """Страница /<username>/<post_id>/edit/ перенаправит
        не автора поста на страницу просмотра поста."""
        response = self.authorized_client2.get('/testuser/100/edit/',
                                               follow=True)
        self.assertRedirects(response,
                             '/testuser/100/')

    def test_urls_uses_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        templates_url_names = {
            'index.html': '/',
            'new.html': '/new/',
            'group.html': '/group/testgroup/'
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_url_post_edit_uses_correct_template(self):
        """URL-адрес /<username>/<post_id>/edit/ использует
        соответствующий шаблон"""
        response = self.authorized_client.get('/testuser/100/edit/')
        self.assertTemplateUsed(response, 'new.html')

    def test_url_404(self):
        """Страница несуществующего поста вернет ответ 404"""
        response = self.guest_client.get('/testuser/101/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
