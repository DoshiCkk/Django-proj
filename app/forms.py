from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import *


class AccountSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'address', 'role']
        widgets = {
            'role': forms.Select(choices=[('buyer', 'Покупатель'), ('seller', 'Продавец')]),
        }

    def __init__(self, *args, **kwargs):
        super(AccountSettingsForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "Логин"
        self.fields['email'].label = "Email"
        self.fields['phone'].label = "Телефон"
        self.fields['address'].label = "Адрес"
        self.fields['role'].label = "Роль"



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['email', 'phone', 'address']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title','description', 'price', 'image', 'category']

class SignUpForm(UserCreationForm):
    class Meta:
        model = Client
        fields = ['username', 'password1', 'password2']

class SignInForm(AuthenticationForm):
    username = forms.CharField(label="логин")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating'] 