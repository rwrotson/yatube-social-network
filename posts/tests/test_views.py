from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.cache import cache

from posts.models import Group, Post, User, Follow, Comment


class TaskPagesTests(TestCase):
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
        cls.other_group = Group.objects.create(
            title='Тестовая группа 2',
            slug='testgroup2',
            description='Тестовое описание второй группы'
        )
        cls.other_post = Post.objects.create(
            text='Тестовый текст для второй группы',
            author=cls.user,
            group=cls.other_group,
            pk=101,
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            pk=100,
        )
        cls.comment = Comment.objects.create(
            text='Текст комментария',
            post=cls.post,
            author=cls.user,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(TaskPagesTests.user)

    def check_post_context(self, first_post):
        self.assertEqual(first_post.text, 'Тестовый текст')
        self.assertEqual(first_post.author, TaskPagesTests.user)
        self.assertEqual(first_post.group, TaskPagesTests.group)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': reverse('index'),
            'new.html': reverse('new_post'),
            'group.html': (reverse('group',
                           kwargs={'slug': 'testgroup'})
                           )
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом
        и проверка того, что при создании поста с указанием
        группы он появляется на главной странице."""
        response = self.authorized_client.get(reverse('index'))
        first_post = response.context['page'][0]
        self.assertIsInstance(first_post, Post)
        self.check_post_context(first_post)

    def test_group_page_shows_correct_context(self):
        """Шаблон group сформирован с правильным контекстом
        и проверка того, что при создании поста с указанием
        группы он появляется в данной группе."""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'testgroup'})
        )
        context = response.context
        self.assertIsInstance(context['group'], Group)
        self.assertIsInstance(context['page'][0], Post)
        group_title = context['group'].title
        group_slug = context['group'].slug
        group_description = context['group'].description
        self.assertEqual(group_title, 'Тестовая группа')
        self.assertEqual(group_slug, 'testgroup')
        self.assertEqual(group_description, 'Тестовое описание группы')
        first_post = response.context['page'][0]
        self.check_post_context(first_post)

    def test_edit_page_shows_correct_context(self):
        """Шаблон edit post сформирован с правильным контекстом"""
        kwargs_dict = {'username': 'testuser', 'post_id': '100'}
        response = self.authorized_client.get(
            reverse('post_edit', kwargs=kwargs_dict)
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_page_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом
        и проверка того, что при создании поста с указанием
        автора он появляется в данном профиле."""
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': 'testuser'})
        )
        context = response.context
        self.assertIsInstance(context['author'], User)
        self.assertIsInstance(context['page'][0], Post)
        profile_title = context['author'].username
        self.assertEqual(profile_title, 'testuser')
        first_post = response.context['page'][0]
        self.check_post_context(first_post)

    def test_post_page_shows_correct_context(self):
        """Шаблон post сформирован с правильным контекстом"""
        kwargs_dict = {'username': 'testuser', 'post_id': '100'}
        response = self.authorized_client.get(
            reverse('post', kwargs=kwargs_dict)
        )
        context = response.context
        self.assertIsInstance(context['author'], User)
        self.assertIsInstance(context['post'], Post)
        self.assertIsInstance(context['comments'][0], Comment)
        author_name = context['author'].username
        self.assertEqual(author_name, 'testuser')
        first_post = context['post']
        self.check_post_context(first_post)
        self.assertEqual(
            context['comments'][0].text, 'Текст комментария')

    def test_new_post_is_not_in_other_group(self):
        """Новый пост с указанием группы не появляется
        на странице другой группы"""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'testgroup2'})
        )
        first_post = response.context['page'][0]
        self.assertNotEqual(first_post, TaskPagesTests.post)

    def test_new_page_shows_correct_context(self):
        """Шаблон new сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_paginator_for_index_page(self):
        """Проверка работы пагинатора"""
        for i in range(12):
            Post.objects.create(
                text=f'Тестовый текст {i}',
                author=self.user2,
                group=self.group,
            )
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)
        response = self.client.get(reverse('index'), {'page': '2'})
        self.assertEqual(len(response.context.get('page').object_list), 4)

    def test_index_cache(self):
        """Кэширование на главной странице работает"""
        response = self.authorized_client.get(reverse('index'))
        first_response = response.content
        Post.objects.create(
            text='Пост для проверки кэширования',
            author=self.user,
        )
        response = self.authorized_client.get(reverse('index'))
        second_response = response.content
        self.assertEqual(first_response, second_response)
        cache.clear()
        response = self.authorized_client.get(reverse('index'))
        second_response = response.content
        self.assertNotEqual(first_response, second_response)

    def test_subscription_follow(self):
        """Авторизованный пользователь может подписываться
        на других пользователей"""
        self.authorized_client.get(reverse(
            'profile_follow', kwargs={'username': 'testuser2'}))
        self.assertTrue(Follow.objects.filter(
            user=self.user, author=self.user2).exists())

    def test_subscription_unfollow(self):
        """Авторизованный пользователь может отписываться
        от других пользователей"""
        Follow.objects.create(user=self.user, author=self.user2)
        self.authorized_client.get(reverse(
            'profile_unfollow', kwargs={'username': 'testuser2'}))
        self.assertFalse(Follow.objects.filter(
            user=self.user, author=self.user2).exists())

    def test_newsfeed(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех,
        кто не подписан на него."""
        Follow.objects.create(user=self.user, author=self.user2)
        Follow.objects.create(user=self.user2, author=self.user)
        Post.objects.create(
            text='Тест работы ленты',
            author=self.user2,
        )
        response = self.authorized_client.get(reverse('follow_index'))
        first_post = response.context['page'][0]
        self.assertEqual(first_post.text, 'Тест работы ленты')
        self.assertEqual(first_post.author, self.user2)
        self.authorized_client.force_login(self.user2)
        response = self.authorized_client.get(reverse('follow_index'))
        first_post = response.context['page'][0]
        self.assertNotEqual(first_post.text, 'Тест работы ленты')
        self.assertNotEqual(first_post.author, self.user2)

    def test_comment_is_not_in_other_post(self):
        """Новый комментарий не появляется
        на странице другого поста"""
        kwargs_dict = {'username': 'testuser', 'post_id': '100'}
        response = self.authorized_client.get(
            reverse('post', kwargs=kwargs_dict)
        )
        Comment.objects.create(
            text='Текст комментария 2',
            post=self.other_post,
            author=self.user,
        )
        context = response.context
        self.assertEqual(
            context['comments'][0].text, 'Текст комментария')

    # тесты для комментариев см в test_forms, спасибо за работу!
