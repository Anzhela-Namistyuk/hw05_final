import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

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

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {reverse('posts:index'): 'posts/index.html',
                                 reverse('posts:group_list', kwargs={
                                     'slug': self.group.slug}):
                                 'posts/group_list.html',
                                 reverse('posts:profile', kwargs={
                                     'username': self.user.username}):
                                 'posts/profile.html',
                                 reverse('posts:post_detail', kwargs={
                                     'post_id': self.post.id}):
                                 'posts/post_detail.html',
                                 reverse('posts:post_edit', kwargs={
                                     'post_id': self.post.id}):
                                 'posts/create_post.html',
                                 reverse('posts:post_create'):
                                 'posts/create_post.html',
                                 '/nonexist-page/':
                                 'core/404.html'
                                 }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_image_0, self.post.image)
        self.assertEqual(post_author_0, self.post.author.username)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.post.group.title)

    def test_group_list_show_correct_context(self):
        """Шаблон group_lis сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        first_object_group = response.context['group']
        first_object = response.context['page_obj'][0]
        group_title_0 = first_object_group.title
        group_slug_0 = first_object_group.slug
        group_description_0 = first_object_group.description
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_image_0, self.post.image)
        self.assertEqual(post_author_0, self.post.author.username)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.post.group.title)
        self.assertEqual(group_title_0, self.group.title)
        self.assertEqual(group_slug_0, self.group.slug)
        self.assertEqual(group_description_0, self.group.description)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_image_0, self.post.image)
        self.assertEqual(post_author_0, self.post.author.username)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.post.group.title)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        first_object = response.context['one_post']
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_image_0, self.post.image)
        self.assertEqual(post_author_0, self.post.author.username)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.post.group.title)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        post_object = response.context['post']
        post_author_0 = post_object.author.username
        post_text_0 = post_object.text
        post_group_0 = post_object.group.title
        self.assertEqual(post_author_0, self.post.author.username)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.post.group.title)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cache.clear()
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        for _ in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый текст',
                group=cls.group,)

    def test_first_page_contains_ten_records(self):
        url_name = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username})
        ]
        for reverse_name in url_name:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                # Проверка: количество постов на первой странице равно 10.
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        url_name = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username})
        ]
        for reverse_name in url_name:
            with self.subTest(reverse_name=reverse_name):
                # Проверка: на второй странице должно быть три поста.
                response = self.client.get((reverse_name) + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)


class PostVerificationTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_2 = User.objects.create_user(username='blogger')
        cls.user_3 = User.objects.create_user(username='Noname')

        cls.group1 = Group.objects.create(
            title='Тестовая группа-1',
            slug='test-slug1',
            description='Тестовое описание-1'
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа-2',
            slug='test-slug2',
            description='Тестовое описание-2'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group1,
        )

    def setUp(self):
        cache.clear()

        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_exist_post_in_page(self):
        url_name = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group1.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for reverse_name in url_name:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context['page_obj'][0]
                post_text_0 = first_object.text
                post_group_0 = first_object.group.title
                self.assertEqual(post_text_0, self.post.text)
                self.assertEqual(post_group_0, self.post.group.title)

    def test_not_exist_post_in_page(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group2.slug}))
        first_object_group = response.context['group']
        group_title_0 = first_object_group.title
        self.assertNotEqual(group_title_0, self.post.group.title)

    def test_cache_index(self):
        post_count = Post.objects.count()
        post_2 = Post.objects.create(
            author=self.user,
            text='Тестовый текст 2-ого поста',

        )
        post_count_new = Post.objects.count()
        response_1 = self.authorized_client.get(reverse('posts:index'))
        response_count = len(response_1.context['page_obj'])
        self.assertEqual(response_count, post_count_new)
        first_object = response_1.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text

        self.assertEqual(post_author_0, post_2.author.username)
        self.assertEqual(post_text_0, post_2.text)

        page_cached = response_1.content
        post_2.delete()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response_2.content, page_cached)
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response_3.content, page_cached)
        response_count_last = len(response_3.context['page_obj'])
        self.assertEqual(response_count_last, post_count)

    def test_profile_follow_unfollow(self):
        response = self.authorized_client_2.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        first_object = response.context['page_obj'][0]
        author = first_object.author
        follow = Follow.objects.create(user=self.user_2, author=author)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user_2,
                author=author
            ).exists()
        )
        follow.delete()

        self.assertFalse(
            Follow.objects.filter(
                user=self.user_2,
                author=author
            ).exists()
        )

    def test_new_post_exists_in_page_follow(self):
        response = self.authorized_client_2.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        first_object = response.context['page_obj'][0]
        author = first_object.author
        Follow.objects.create(user=self.user_2, author=author)

        response_1 = self.authorized_client_2.get(reverse(
            'posts:follow_index')
        )
        response_count_1 = len(response_1.context['page_obj'])

        new_post = Post.objects.create(
            author=self.user,
            text='Тестовый текст 3 поста'
        )

        response_2 = self.authorized_client_2.get(reverse(
            'posts:follow_index')
        )
        response_count_2 = len(response_2.context['page_obj'])
        self.assertEqual(response_count_2, response_count_1 + 1)

        first_object = response_2.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        self.assertEqual(post_author_0, new_post.author.username)
        self.assertEqual(post_text_0, new_post.text)
