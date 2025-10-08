# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from django.conf import settings

class User(AbstractUser):
    avatar = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    theme = models.CharField(max_length=10, choices=[("light", "Light"), ("dark", "Dark")], default="light")


    def __str__(self):
        return self.username
    
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    image = models.URLField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.JSONField(default=list, blank=True)  # ["tech", "uzb"]
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    saved_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='saved_posts', blank=True)
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# blog/models.py (below Post)
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    likes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} on {self.post.title}"
