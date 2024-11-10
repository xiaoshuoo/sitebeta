from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, InviteCode, Post, Category

class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'editor-dark w-full min-h-[500px] bg-[#1E1E1E] text-white font-mono p-4 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/50',
            'style': 'resize: none; line-height: 1.6; font-family: "JetBrains Mono", monospace;',
            'placeholder': 'Введите содержание поста...',
            'id': 'content-editor'
        }),
        required=True
    )
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'thumbnail', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full bg-transparent border-none text-xl text-white placeholder-gray-500 focus:outline-none focus:ring-0',
                'placeholder': 'Введите заголовок...',
                'style': 'font-family: "JetBrains Mono", monospace;',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': '''
                    w-full bg-[#2d2a3d] text-white rounded-lg 
                    border border-gray-700 focus:border-primary-500 
                    focus:ring-2 focus:ring-primary-500/50 
                    py-2.5 px-4 appearance-none cursor-pointer
                    hover:bg-[#363248] transition-all duration-200
                    text-sm font-medium
                ''',
                'style': '''
                    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%238b5cf6' width='24' height='24'%3E%3Cpath d='M7 10l5 5 5-5z'/%3E%3C/svg%3E");
                    background-repeat: no-repeat;
                    background-position: right 0.75rem center;
                    background-size: 1.25rem;
                    padding-right: 2.5rem;
                    -webkit-appearance: none;
                    -moz-appearance: none;
                ''',
                'required': True
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'sr-only peer'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем пустой выбор для категории с кастомным текстом
        self.fields['category'].empty_label = "Выберите категорию..."
        
        # Добавляем классы для опций в выпадающем списке
        self.fields['category'].widget.attrs['class'] += '''
            [&>option]:bg-[#2d2a3d]
            [&>option]:text-white
            [&>option:hover]:bg-primary-500
            [&>option:checked]:bg-primary-500
        '''

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        content = cleaned_data.get('content')
        category = cleaned_data.get('category')

        if not title:
            raise forms.ValidationError('Пожалуйста, введите заголовок поста.')
        if not content:
            raise forms.ValidationError('Пожалуйста, введите содержание поста.')
        if not category:
            raise forms.ValidationError('Пожалуйста, выберите категорию.')

        return cleaned_data

class CustomUserCreationForm(UserCreationForm):
    invite_code = forms.CharField(
        max_length=20, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-[#2d2a3d] border border-gray-700 text-white rounded-lg focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 py-2.5 px-4',
            'placeholder': 'Введите код приглашения'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'invite_code')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full bg-[#2d2a3d] border border-gray-700 text-white rounded-lg focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 py-2.5 px-4',
                'placeholder': 'Введите имя пользователя'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full bg-[#2d2a3d] border border-gray-700 text-white rounded-lg focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 py-2.5 px-4',
            'placeholder': 'Введите пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full bg-[#2d2a3d] border border-gray-700 text-white rounded-lg focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 py-2.5 px-4',
            'placeholder': 'Подтвердите пароль'
        })

    def clean_invite_code(self):
        code = self.cleaned_data.get('invite_code')
        try:
            invite = InviteCode.objects.get(code=code, is_active=True, used_by__isnull=True)
            return invite
        except InviteCode.DoesNotExist:
            raise forms.ValidationError("Недействительный код приглашения")

class UserProfileForm(forms.ModelForm):
    bio = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full bg-[#2d2a3d] border border-gray-700 rounded-lg p-4 text-white focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500',
            'rows': '4',
            'placeholder': 'Расскажите о себе...'
        }),
        required=False
    )
    
    website = forms.URLField(
        widget=forms.URLInput(attrs={
            'class': 'w-full bg-[#2d2a3d] border border-gray-700 text-white rounded-lg focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 py-2 px-3',
            'placeholder': 'https://'
        }),
        required=False
    )
    
    location = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-[#2d2a3d] border border-gray-700 text-white rounded-lg focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 py-2 px-3',
            'placeholder': 'Город, Страна'
        }),
        required=False
    )
    
    avatar = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'accept': 'image/*'
        }),
        required=False
    )

    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'website', 'location']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'avatar':
                self.fields[field].label_class = 'block text-sm font-medium text-gray-400 mb-2'