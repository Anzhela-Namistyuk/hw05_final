from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from django.views.decorators.cache import cache_page

from yatube.settings import PAGE_POST

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def get_paginator(request, posts_list):
    paginator = Paginator(posts_list, PAGE_POST)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(20)
def index(request):
    posts_list = Post.objects.all()
    page_obj = get_paginator(request, posts_list)
    context = {
        'page_obj': page_obj,
        'title': 'Главная страница',
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.group_posts.all()
    page_obj = get_paginator(request, posts_list)
    title = f'Записи сообщества {group.title}'
    context = {
        'page_obj': page_obj,
        'group': group,
        'title': title,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_list = author.posts.all()
    page_obj = get_paginator(request, posts_list)

    following = author.following.exists()

    context = {
        'page_obj': page_obj,
        'author': author,
        'count_post': posts_list.count(),
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    one_post = get_object_or_404(Post, pk=post_id)
    count_post = one_post.author.posts.count()
    comments = one_post.comments.all()
    comment_form = CommentForm()
    context = {
        'one_post': one_post,
        'count_post': count_post,
        'form': comment_form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method != 'POST':
        form = PostForm()
        return render(request, 'posts/create_post.html', {'form': form})

    form = PostForm(request.POST, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)

    return render(request, 'posts/create_post.html', {'form': form})


def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    user = request.user
    followings = user.follower.values_list('author', flat=True)
    posts_list = Post.objects.filter(author__in=followings)
    page_obj = get_paginator(request, posts_list)
    context = {
        'page_obj': page_obj,
        'title': 'Подписки на посты'
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if user != author:
        Follow.objects.get_or_create(user=user, author=author)
        return redirect('posts:profile', username=username)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user, author__username=username).delete()
    return redirect('posts:profile', username=username)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
