from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Category, Tag, InviteCode, Profile, Comment, Story
from django.template.defaultfilters import slugify
import uuid

class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={'id': 'editor'}),
        required=True
    )
    
    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-6 py-4 bg-[#1a1625] border border-purple-500/20 rounded-xl text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all duration-300 hover:border-purple-500/40',
            'placeholder': '✨ Введите название поста',
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all().order_by('name'),
        required=True,
        empty_label="Выберите категорию",
        widget=forms.Select(attrs={
            'class': 'w-full px-6 py-4 bg-[#1a1625] border border-purple-500/20 rounded-xl text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all duration-300 hover:border-purple-500/40',
        })
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all().order_by('name'),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'w-full px-6 py-4 bg-[#1a1625] border border-purple-500/20 rounded-xl text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all duration-300 hover:border-purple-500/40',
            'size': '5',
        })
    )
    
    thumbnail = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'id': 'thumbnail-upload',
            'accept': 'image/*',
        })
    )
    
    is_published = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox h-5 w-5 text-purple-500 rounded border-purple-500/20 focus:ring-purple-500/20 focus:ring-2 transition-all duration-300',
        })
    )
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'tags', 'thumbnail', 'is_published']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-surface/50 border border-white/10 rounded-lg text-white'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'w-full px-4 py-3 bg-surface/50 border border-white/10 rounded-lg text-white'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Загружаем все категории и теги заранее
        self.fields['category'].queryset = Category.objects.all().order_by('name')
        self.fields['tags'].queryset = Tag.objects.all().order_by('name')
        
        # Добавляем подсказки для полей
        self.fields['title'].help_text = 'Придумайте привлекательный заголовок для вашего поста'
        self.fields['category'].help_text = 'Выберите наиболее подходящую категорию'
        self.fields['tags'].help_text = 'Выберите теги для лучшей навигации (Ctrl+Click для множественного выбора)'
        self.fields['thumbnail'].help_text = 'Рекомендуемый размер: 1200x630px'
        self.fields['is_published'].help_text = 'Отметьте для немедленной публикации'

        # Проверяем наличие категорий и тегов
        if not self.fields['category'].queryset.exists():
            self.fields['category'].help_text = 'Нет доступных категорий. Обратитесь к администратору.'
        
        if not self.fields['tags'].queryset.exists():
            self.fields['tags'].help_text = 'Нет доступных тегов. Обратитесь к администратору.'

    def clean(self):
        cleaned_data = super().clean()
        
        # Проверяем обязательные поля
        if not cleaned_data.get('title'):
            self.add_error('title', 'Это поле обязательно.')
        
        if not cleaned_data.get('content'):
            self.add_error('content', 'Это поле обязательно.')
        
        if not cleaned_data.get('category'):
            self.add_error('category', 'Выберите категорию.')
        
        return cleaned_data

    def clean_thumbnail(self):
        thumbnail = self.cleaned_data.get('thumbnail')
        if thumbnail:
            # Проверяем размер файла
            if thumbnail.size > 10 * 1024 * 1024:  # 10MB
                raise forms.ValidationError('Размер файла не должен превышать 10MB')
            
            # Проверяем MIME-тип файла
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if not hasattr(thumbnail, 'content_type') or thumbnail.content_type not in allowed_types:
                raise forms.ValidationError('Поддерживаются только форматы JPG, PNG и GIF')
            
            # Проверяем, что это действительно изображение
            try:
                from PIL import Image
                img = Image.open(thumbnail)
                img.verify()  # Проверяем, что файл является валидным изображением
                
                # Открываем изображение заново после verify()
                thumbnail.seek(0)
                img = Image.open(thumbnail)
                
                # Проверяем разрешение для не-GIF изображений
                if thumbnail.content_type != 'image/gif':
                    width, height = img.size
                    max_dimension = 5000  # Максимальный размер стороны
                    if width > max_dimension or height > max_dimension:
                        raise forms.ValidationError(f'Максимальный размер изображения - {max_dimension}x{max_dimension} пикселей')
                
                # Сбрасываем указатель файла в начало
                thumbnail.seek(0)
            except Exception as e:
                raise forms.ValidationError(f'Ошибка при обработке изображения: {str(e)}')
            
        return thumbnail

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'website', 'occupation', 'avatar', 'cover']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-surface/50 border border-white/10 rounded-lg text-white placeholder-gray-500',
                'rows': 4,
                'placeholder': '✍️ Расскажите о себе...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-surface/50 border border-white/10 rounded-lg text-white placeholder-gray-500',
                'placeholder': '📍 Ваше местоположение'
            }),
            'website': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 bg-surface/50 border border-white/10 rounded-lg text-white placeholder-gray-500',
                'placeholder': '🌐 Ваш веб-сайт'
            }),
            'occupation': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-surface/50 border border-white/10 rounded-lg text-white placeholder-gray-500',
                'placeholder': '💼 Род деятельности'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*'
            }),
            'cover': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*',
                'id': 'id_cover'
            })
        }

    def clean_cover(self):
        cover = self.cleaned_data.get('cover')
        if cover and not isinstance(cover, str):
            if hasattr(cover, 'size'):
                if cover.size > 10 * 1024 * 1024:
                    raise forms.ValidationError('Размер файла не должен превышать 10MB')
            if hasattr(cover, 'content_type'):
                if not cover.content_type.startswith('image/'):
                    raise forms.ValidationError('Файл должен быть изображением')
        return cover

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and not isinstance(avatar, str):  # Проверяем только новые файлы
            if hasattr(avatar, 'size'):  # Проверяем размер только для новых файлов
                if avatar.size > 5 * 1024 * 1024:  # 5MB
                    raise forms.ValidationError('Размер файла не должен превышать 5MB')
            if hasattr(avatar, 'content_type'):  # Проверяем тип только для новых файлов
                if not avatar.content_type.startswith('image/'):
                    raise forms.ValidationError('Файл должен быть изображением')
        return avatar

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-6 py-4 bg-surface-700/30 border border-purple-500/20 rounded-xl text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all duration-300 hover:border-purple-500/40',
            'placeholder': '👤 Выберите имя пользователя'
        })
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-6 py-4 bg-surface-700/30 border border-purple-500/20 rounded-xl text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all duration-300 hover:border-purple-500/40',
            'placeholder': '🔒 Придумайте пароль'
        })
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-6 py-4 bg-surface-700/30 border border-purple-500/20 rounded-xl text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all duration-300 hover:border-purple-500/40',
            'placeholder': '🔒 Повторите пароль'
        })
    )
    
    invite_code = forms.CharField(
        max_length=8,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-6 py-4 bg-surface-700/30 border border-purple-500/20 rounded-xl text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all duration-300 hover:border-purple-500/40 uppercase',
            'placeholder': '🎟️ Введите инвайт-код'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'invite_code')

    def clean_invite_code(self):
        code = self.cleaned_data.get('invite_code')
        try:
            invite = InviteCode.objects.get(code=code, is_active=True)
            if invite.used_by:
                raise forms.ValidationError('Этот инвайт-код уже использован')
            return code
        except InviteCode.DoesNotExist:
            raise forms.ValidationError('Недействительный инвайт-код')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            invite = InviteCode.objects.get(code=self.cleaned_data['invite_code'])
            invite.use(user)
        return user

class ProfileUpdateForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-6 py-4 bg-[#1a1625] border border-purple-500/20 rounded-xl text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all duration-300 hover:border-purple-500/40',
            'placeholder': 'Введите новый никнейм'
        })
    )

    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'id': 'avatar-upload',
            'accept': 'image/*'
        })
    )
    
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-6 py-4 bg-surface-700/30 border border-purple-500/20 rounded-xl text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all duration-300 hover:border-purple-500/40',
            'placeholder': '✍️ Расскажите о себе...',
            'rows': 4
        })
    )
    
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-6 py-4 bg-surface-700/30 border border-purple-500/20 rounded-xl text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all duration-300 hover:border-purple-500/40',
            'placeholder': '📍 Ваше местоположение'
        })
    )
    
    occupation = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-6 py-4 bg-surface-700/30 border border-purple-500/20 rounded-xl text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all duration-300 hover:border-purple-500/40',
            'placeholder': '💼 Ваша профессия или род занятий'
        })
    )
    
    class Meta:
        model = Profile
        fields = ['username', 'avatar', 'cover', 'bio', 'location', 'occupation', 'website']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.exclude(pk=self.instance.user.pk).filter(username=username).exists():
            raise forms.ValidationError('Этот никнейм уже занят')
        return username

class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-6 py-4 bg-surface-700/30 border border-purple-500/20 rounded-xl text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all duration-300 hover:border-purple-500/40',
            'placeholder': '✍️ Напишите комментарий...',
            'rows': 3
        }),
        required=True
    )

    class Meta:
        model = Comment
        fields = ['content']

    def clean_content(self):
        content = self.cleaned_data.get('content', '').strip()
        if not content:
            raise forms.ValidationError('Комментарий не может быть пустым')
        if len(content) > 1000:  # Ограничение на длину комментария
            raise forms.ValidationError('Комментарий слишком длинный (максимум 1000 символов)')
        return content

    def save(self, commit=True):
        comment = super().save(commit=False)
        if commit:
            comment.save()
        return comment

class StoryForm(forms.ModelForm):
    tags = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'w-full px-6 py-4 bg-surface-700/30 border border-purple-500/20 rounded-xl text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all duration-300 hover:border-purple-500/40',
            'placeholder': '✨ Введите хештеги через запятую'
        })
    )
    
    class Meta:
        model = Story
        fields = ['cover', 'title', 'chapters_count', 'tags', 'description', 'link_title', 'link_url']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-6 py-4 bg-surface-700/30 border border-purple-500/20 rounded-xl text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all duration-300 hover:border-purple-500/40',
                'placeholder': '✨ Введите название истории'
            }),
            'chapters_count': forms.NumberInput(attrs={
                'class': 'w-full px-6 py-4 bg-surface-700/30 border border-purple-500/20 rounded-xl text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all duration-300 hover:border-purple-500/40',
                'placeholder': '📚 Количество глав',
                'min': '0',
                'style': 'color: white; background-color: rgba(26, 22, 37, 0.3);'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-6 py-4 bg-surface-700/30 border border-purple-500/20 rounded-xl text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all duration-300 hover:border-purple-500/40',
                'placeholder': '✍️ Опишите вашу историю...',
                'rows': '6'
            }),
            'link_title': forms.TextInput(attrs={
                'class': 'w-full px-6 py-4 bg-surface-700/30 border border-purple-500/20 rounded-xl text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all duration-300 hover:border-purple-500/40',
                'placeholder': '🔖 Название ссылки'
            }),
            'link_url': forms.URLInput(attrs={
                'class': 'w-full px-6 py-4 bg-surface-700/30 border border-purple-500/20 rounded-xl text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all duration-300 hover:border-purple-500/40',
                'placeholder': '🔗 https://example.com'
            }),
            'cover': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*'
            })
        }
    
    def clean_tags(self):
        tags_str = self.cleaned_data.get('tags', '')
        if not tags_str:
            return []
        tag_names = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        tags = []
        for tag_name in tag_names:
            if not tag_name:  # Пропускаем пустые теги
                continue
            try:
                tag = Tag.objects.get(name=tag_name)
            except Tag.DoesNotExist:
                # Генерируем уникальный slug
                slug = slugify(tag_name)
                if not slug:  # Если slugify вернул пустую строку
                    slug = f"tag-{uuid.uuid4().hex[:8]}"
                counter = 1
                original_slug = slug
                while Tag.objects.filter(slug=slug).exists():
                    slug = f"{original_slug}-{counter}"
                    counter += 1
                tag = Tag.objects.create(name=tag_name, slug=slug)
            tags.append(tag)
        return tags
    
    def save(self, commit=True):
        story = super().save(commit=False)
        
        # Собираем дополнительные названия
        alt_titles = []
        for key, value in self.data.items():
            if key.startswith('alt_title_') and value.strip():
                alt_titles.append(value.strip())
        story.alt_titles = alt_titles
        
        # Собираем дополнительные ссылки
        additional_links = []
        for key, value in self.data.items():
            if key.startswith('link_title_'):
                link_id = key.split('_')[-1]
                url_key = f'link_url_{link_id}'
                if url_key in self.data and self.data[url_key].strip() and value.strip():
                    additional_links.append({
                        'title': value.strip(),
                        'url': self.data[url_key].strip()
                    })
        story.additional_links = additional_links
        
        if commit:
            story.save()
            story.tags.clear()
            story.tags.add(*self.cleaned_data['tags'])
        return story