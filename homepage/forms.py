from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from .models import Comment
from django import forms


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'body')


class LoginForm(AuthenticationForm):
    username = UsernameField(
        label='Email or Username',
        widget=forms.TextInput(attrs={'autofocus': True})
    )
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match")
        return cd['password2']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        help_texts = {
            'username': '150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        }


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ()
