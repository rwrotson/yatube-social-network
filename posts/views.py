from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from posts.models import Post, Group, User, Comment, Follow
from posts.forms import PostForm, CommentForm


def index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "index.html", {"page": page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page})


@login_required
def new_post(request):
    if request.method != "POST":
        form = PostForm()
        return render(request, "new.html", {"form": form})
    form = PostForm(request.POST)
    if not form.is_valid():
        return render(request, "new.html", {"form": form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("index")


def profile(request, username):
    author = get_object_or_404(User, username=username)
    if not request.user.is_authenticated:
        following = False
    else:
        following = Follow.objects.filter(
            author=author, user=request.user).exists()
    posts = author.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "profile.html",
                  {"author": author, "page": page, "following": following})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    author = post.author
    comments = Comment.objects.filter(post=post)
    if not request.user.is_authenticated:
        following = False
    else:
        following = Follow.objects.filter(
            author=author, user=request.user).exists()
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        form.save()
        return redirect("add_comment", username, post_id)
    context = {"form": form, "post": post, "author": author,
               "comments": comments, "is_comment": True,
               "following": following}
    return render(request, "post.html", context)


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    author = post.author
    if author != request.user:
        return redirect("post",
                        username=author.username, post_id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if not form.is_valid():
        context = {"author": author, "post": post,
                   "form": form, "is_edit": True}
        return render(request, "new.html", context)
    post.save()
    return redirect("post", username=request.user.username, post_id=post_id)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    author = post.author
    comments = Comment.objects.filter(post=post)
    following = Follow.objects.filter(
        author=author, user=request.user).exists()
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        form.save()
        return redirect("add_comment", username, post_id)
    context = {"form": form, "post": post, "author": author,
               "comments": comments, "is_comment": True,
               "following": following}
    return render(request, "post.html", context)


@login_required
def follow_index(request):
    latest = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(latest, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {"page": page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(author=author, user=request.user)
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(author=author, user=request.user).delete()
    return redirect('profile', username)


def page_not_found(request, exception):
    return render(request, "misc/404.html",
                  {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
