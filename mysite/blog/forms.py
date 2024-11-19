from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Category, Tag, InviteCode, Profile

class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'id': 'content-editor',
            'class': 'tinymce',
            'style': 'min-height: 400px;'
        }),
        required=False,
    )
    
    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-6 py-4 bg-[#1a1625] border border-purple-500/20 rounded-xl text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all duration-300 hover:border-purple-500/40',
            'placeholder': '✨ Введите название поста',
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-6 py-4 bg-[#1a1625] border border-purple-500/20 rounded-xl text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all duration-300 hover:border-purple-500/40',
        })
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'w-full px-6 py-4 bg-[#1a1625] border border-purple-500/20 rounded-xl text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all duration-300 hover:border-purple-500/40',
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_published'].initial = True
        
        # Добавляем подсказки для полей
        self.fields['title'].help_text = 'Придумайте привлекательный заголовок для вашего поста'
        self.fields['category'].help_text = 'Выберите наиболее подходящую категорию'
        self.fields['tags'].help_text = 'Выберите несколько тегов для лучшей навигации (Ctrl+Click для множественного выбора)'
        self.fields['thumbnail'].help_text = 'Рекомендуемый размер: 1200x630px'
        self.fields['is_published'].help_text = 'Отметьте для немедленной публикации'
        
        # Оптимизируем запрос категорий
        self.fields['category'].queryset = Category.objects.only('id', 'name')

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise forms.ValidationError('Это поле обязательно.')
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content', '').strip()
        return content

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError('Выберите категорию.')
        return category

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

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
        fields = ['avatar', 'bio', 'location', 'occupation']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем подсказки для полей
        self.fields['avatar'].help_text = 'Рекомендуемый размер: 400x400px'
        self.fields['bio'].help_text = 'Максимум 500 символов'
        self.fields['location'].help_text = 'Например: Москва, Россия'
        self.fields['occupation'].help_text = 'Например: Web Developer'