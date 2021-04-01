import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus

from posts.models import Post, User, Comment


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(username='testuser')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста',
            pk=100,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_postform_create_post(self):
        """Форма new_post создает новую запись в модели
        и перенаправляет на главную страницу"""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'author': PostFormTests.user,
            'text': 'Тестовый текст 2',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(
            text='Тестовый текст 2', author=PostFormTests.user,).exists()
        )

    def test_postform_guest_doesnt_create_post(self):
        """Форма new_post не создает новую запись в модели
        для неавторизированного пользователя"""
        posts_count = Post.objects.count()
        form_data = {
            'author': PostFormTests.user,
            'text': 'Тестовый текст 2',
        }
        response = self.guest_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_post_edit_changes_post(self):
        """Форма edit_post меняет запись в модели
        и перенаправляет на страницу просмотра поста"""
        kwargs_dict = {'username': 'testuser', 'post_id': '100'}
        form_data = {'text': 'Тестовый текст 2'}
        response = self.authorized_client.post(
            reverse('post_edit', kwargs=kwargs_dict),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse('post', kwargs=kwargs_dict))
        post = Post.objects.get(pk=100)
        self.assertEqual(post.text, 'Тестовый текст 2')

    def test_commentform_creates_comment(self):
        """Авторизированный пользователь может комментировать посты"""
        comments_count = Comment.objects.filter(post=self.post).count()
        kwargs = {'username': 'testuser', 'post_id': '100'}
        response = self.authorized_client.post(
            reverse('add_comment', kwargs=kwargs),
            data={'text': 'Текст комментария'},
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        comments_count2 = Comment.objects.filter(post=self.post).count()
        self.assertEqual(comments_count + 1, comments_count2)
        self.assertEqual(Comment.objects.filter(
            post=self.post)[0].text, 'Текст комментария')

    def test_commentform_doesnt_create_comment(self):
        """Гостевой пользователь не может комментировать посты"""
        comments_count = Comment.objects.filter(post=self.post).count()
        kwargs = {'username': 'testuser', 'post_id': '100'}
        response = self.guest_client.post(
            reverse('add_comment', kwargs=kwargs),
            data={'text': 'Текст комментария'},
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        comments_count2 = Comment.objects.filter(post=self.post).count()
        self.assertEqual(comments_count, comments_count2)
