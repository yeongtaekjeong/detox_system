from django import forms
from django.contrib.auth.forms import UserCreationForm
from detoxapp.models import User


#"name", "username", "email", "password", "phone", "join_date"
class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["name", "username", "password1", "password2", "email", "phone", "join_date"]
        widgets = {
            'name' : forms.TextInput(),
            'username' : forms.TextInput(),       
            'password1' : forms.PasswordInput(),
            'password2' : forms.PasswordInput(),
            'email' : forms.EmailInput(),
            'phone' : forms.TextInput(),
            'join_date' : forms.TextInput(),
        }
        labels = {
            "name" : '성명', 
            "username" : '아이디', 
            "password1" : '비밀번호', 
            'password2' : '비밀번호확인',
            "email" : '이메일', 
            "phone" : '전화번호',
            "join_date":'가입일',
        }
