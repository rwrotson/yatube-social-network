from django.test import TestCase
from django.contrib.auth import get_user_model

from posts.models import Post, Group, User, Comment

User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser')
        cls.group = Group.objects.create(
            title='Название тестовой группы',
            slug='Ссылка на тестовую группу',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста',
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            text='t' * 20,
            post=cls.post,
            author=cls.user,
        )

    def test_verbose_name(self):
        """Правильность значений verbose_name поста"""
        post = PostFormTest.post
        field_verboses = {
            'group': 'Имя группы',
            'text': 'Текст поста',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """Правильность значений help_text поста"""
        post = PostFormTest.post
        help_text = {
            'group': 'Введите имя группы',
            'text': 'Введите текст поста',
        }
        for value, expected in help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_comments_verbose_name(self):
        """Правильность значений verbose_name комментария"""
        expected = 'Текст комментария'
        value = self.comment._meta.get_field('text').verbose_name
        self.assertEqual(expected, value)

    def test_comments_help_text(self):
        """Правильность значений help_text комментария"""
        expected = 'Введите текст комментария'
        value = self.comment._meta.get_field('text').help_text
        self.assertEqual(expected, value)

    def test_post_str(self):
        """Правильность метода __str__ для Post"""
        post = PostFormTest.post
        expected = post.text[:15]
        self.assertEqual(str(post), expected)

    def test_group_str(self):
        """Правильность метода __str__ для Group"""
        group = PostFormTest.group
        expected = group.title
        self.assertEqual(str(group), expected)

    def test_comment_str(self):
        """Правильность метода __str__ для Comment"""
        self.assertEqual(str(self.comment), 't' * 15)
