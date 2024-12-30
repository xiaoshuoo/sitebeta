from django.contrib import admin
from .models import Category, Post, Tag, InviteCode, Profile, PostView, Title, TextTemplate

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'posts_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_filter = ['name']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'created_at', 'is_published', 'views_count']
    list_filter = ['is_published', 'category', 'created_at']
    search_fields = ['title', 'content']
    raw_id_fields = ['author']
    date_hierarchy = 'created_at'
    list_editable = ['is_published']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(InviteCode)
class InviteCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'created_by', 'created_at', 'is_active', 'used_by']
    list_filter = ['created_at', 'is_active']
    search_fields = ['code', 'created_by__username', 'used_by__username']
    readonly_fields = ['code', 'created_at']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # если редактируем существующий объект
            return self.readonly_fields + ['created_by', 'used_by']
        return self.readonly_fields

@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'icon', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Стилизация', {
            'fields': ('color', 'icon'),
            'classes': ('collapse',)
        })
    )

    def save_model(self, request, obj, form, change):
        if not obj.icon.startswith('fas fa-'):
            obj.icon = f'fas fa-{obj.icon}'
        super().save_model(request, obj, form, change)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'occupation', 'get_titles')
    search_fields = ('user__username', 'location', 'occupation')
    filter_horizontal = ('titles',)
    
    def get_titles(self, obj):
        return ", ".join([title.name for title in obj.titles.all()])
    get_titles.short_description = 'Титулы'

@admin.register(PostView)
class PostViewAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['post__title', 'user__username']

@admin.register(TextTemplate)
class TextTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_by', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content', 'category')
    date_hierarchy = 'created_at'
