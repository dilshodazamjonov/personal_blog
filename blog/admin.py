from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Category, Post, Comment


# --- Custom User Admin ---
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "is_staff", "theme", "joined_at")
    list_filter = ("is_staff", "is_superuser", "theme", "joined_at")
    search_fields = ("username", "email")
    readonly_fields = ("joined_at",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "avatar", "bio")}),
        ("Preferences", {"fields": ("theme",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "joined_at")}),
    )


# --- Category Admin ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


# --- Post Admin ---
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "views", "likes", "created_at", "updated_at")
    list_filter = ("category", "author", "created_at")
    search_fields = ("title", "content", "tags")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("views", "likes", "created_at", "updated_at")
    raw_id_fields = ("author",)
    autocomplete_fields = ("category",)
    filter_horizontal = ("saved_by", "liked_by")

    fieldsets = (
        ("Basic Info", {"fields": ("author", "title", "slug", "content", "image", "category")}),
        ("Metadata", {"fields": ("tags", "views", "likes")}),
        ("Relations", {"fields": ("saved_by", "liked_by")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


# --- Comment Admin ---
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "post", "short_text", "likes", "created_at")
    list_filter = ("created_at", "author")
    search_fields = ("text", "author__username", "post__title")
    readonly_fields = ("created_at",)
    raw_id_fields = ("post", "author")

    def short_text(self, obj):
        return (obj.text[:50] + "...") if len(obj.text) > 50 else obj.text
    short_text.short_description = "Comment Text"
