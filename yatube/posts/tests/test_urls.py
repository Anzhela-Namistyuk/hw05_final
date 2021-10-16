from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test__author_tech(self):
        url_names = {'/about/author/', '/about/tech/'}
        for adress in url_names:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестове описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='auth')
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(PostURLTests.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/':
            'posts/group_list.html',
            f'/profile/{self.user.username}/':
            'posts/profile.html',
            f'/posts/{self.post.id}/':
            'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/':
            'posts/create_post.html',
            '/create/':
            'posts/create_post.html',
            '/follow/':
            'posts/follow.html',
        }

        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client2.get(adress)
                self.assertTemplateUsed(response, template)

    def test_non_page(self):
        responses = [
            self.guest_client.get('/unexisting_page/'),
            self.authorized_client.get('/unexisting_page/'),
            self.authorized_client2.get('/unexisting_page/')
        ]
        for response in responses:
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_non_authorized_page(self):
        addresses = {
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.id}/'
        }

        for adress in addresses:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_page(self):
        addresses = {
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.id}/',
            '/create/'
        }
        for adress in addresses:
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_page(self):
        adress = f'/posts/{self.post.id}/edit/'
        response = self.authorized_client2.get(adress)
        response1 = self.authorized_client.get(adress)
        response2 = self.guest_client.get(adress)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response1.status_code, HTTPStatus.FOUND)
        self.assertEqual(response2.status_code, HTTPStatus.FOUND)
