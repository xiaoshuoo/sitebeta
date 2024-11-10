from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, InviteCode, Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'thumbnail', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full bg-gray-700 bg-opacity-50 text-white rounded-lg border border-gray-600 focus:border-purple-500 focus:ring-2 focus:ring-purple-500 px-4 py-3 transition duration-300',
                'placeholder': 'Введите заголовок поста'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full bg-gray-700 bg-opacity-50 text-white rounded-lg border border-gray-600 focus:border-purple-500 focus:ring-2 focus:ring-purple-500 px-4 py-3 transition duration-300'
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full bg-gray-700 bg-opacity-50 text-white border border-gray-600 focus:border-purple-500 focus:ring-2 focus:ring-purple-500 transition duration-300'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'sr-only peer'
            })
        }

class CustomUserCreationForm(UserCreationForm):
    invite_code = forms.CharField(max_length=20, required=True, label='Код приглашения')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'invite_code')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def clean_invite_code(self):
        code = self.cleaned_data.get('invite_code')
        try:
            invite = InviteCode.objects.get(code=code, is_active=True, used_by__isnull=True)
            return invite
        except InviteCode.DoesNotExist:
            raise forms.ValidationError("Недействительный код приглашения")

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('avatar', 'bio', 'website', 'location', 'interests')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'interests': forms.CheckboxSelectMultiple()
        }