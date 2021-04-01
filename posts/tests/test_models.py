from django.test import TestCase

from posts.models import Post, Group, User


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Название тестовой группы',
            slug='Ссылка на тестовую группу',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=User.objects.create(username='Имя-тест'),
            text='Тестовый текст поста',
            group=cls.group,
        )

    def test_verbose_name(self):
        """Правильность значений verbose_name"""
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
        """Правильность значений help_text"""
        post = PostFormTest.post
        help_text = {
            'group': 'Введите имя группы',
            'text': 'Введите текст поста',
        }
        for value, expected in help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

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
