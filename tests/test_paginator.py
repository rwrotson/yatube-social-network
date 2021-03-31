import pytest
from django.core.paginator import Page, Paginator

pytestmark = [pytest.mark.django_db]

class TestGroupPaginatorView:

    def test_group_paginator_view_get(self, client, few_posts_with_group):
        try:
            response = client.get(f'/group/{few_posts_with_group.group.slug}')
        except Exception as e:
            assert False, f'''Страница `/group/<slug>/` работает неправильно. Ошибка: `{e}`'''
        if response.status_code in (301, 302):
            response = client.get(f'/group/{few_posts_with_group.group.slug}/')
        assert response.status_code != 404, 'Страница `/group/<slug>/` не найдена, проверьте этот адрес в *urls.py*'
        assert 'page' in response.context, (
            'Проверьте, что передали переменную `page` в контекст страницы `/group/<slug>/`'
        )
        assert isinstance(response.context['page'], Page), (
            'Проверьте, что переменная `page` на странице `/group/<slug>/` типа `Page`'
        )

    def test_group_paginator_not_in_context_view(self, client, post_with_group):
        response = client.get(f'/group/{post_with_group.group.slug}/')
        assert response.status_code != 404, 'Страница `/group/<slug>/` не найдена, проверьте этот адрес в *urls.py*'
        assert 'paginator' not in response.context, (
            'Проверьте, что переменной `paginator` нет в контексте страницы `/group/<slug>/`'
        )
        assert isinstance(response.context['page'].paginator, Paginator), (
            'Проверьте, что переменная `paginator` на странице `/group/<slug>/` типа `Paginator`'
        )

    def test_index_paginator_not_in_view_context(self, client, few_posts_with_group):
        response = client.get('/')
        assert 'paginator' not in response.context, (
            'Проверьте, что объект `page` страницы `/` не содержит `paginator` в контексте'
        )
        assert isinstance(response.context['page'].paginator, Paginator), (
            'Проверьте, что переменная `paginator` объекта `page` на странице `/` типа `Paginator`'
        )

    def test_index_paginator_view(self, client, post_with_group):
        response = client.get('/')
        assert response.status_code != 404, 'Страница `/` не найдена, проверьте этот адрес в *urls.py*'
        assert 'page' in response.context, (
            'Проверьте, что передали переменную `page` в контекст страницы `/`'
        )
        assert isinstance(response.context['page'], Page), (
            'Проверьте, что переменная `page` на странице `/` типа `Page`'
        )

    def test_profile_paginator_view(self, client, few_posts_with_group):
        response = client.get(f'/{few_posts_with_group.author.username}/')
        assert 'paginator' not in response.context, (
            'Проверьте, что объект `page` страницы `/` не содержит `paginator` в контексте'
        )
        assert isinstance(response.context['page'].paginator, Paginator), (
            'Проверьте, что переменная `paginator` объекта `page` на странице `/` типа `Paginator`'
        )
