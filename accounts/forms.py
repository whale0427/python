from django import forms

ROLE_CHOICES=[
    ("admin","管理员"),
    ("teacher","老师"),
    ("student","学生"),
]
class LoginForm(forms.Form):
    username=forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'请输入用户'}),
    )
    password=forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'请输入密码'}),
    )
    role=forms.ChoiceField(label="身份",choices=ROLE_CHOICES)

    def clean_username(self):
        username=self.cleaned_data["username"]
        if not username:
            raise forms.ValidationError("用户不允许为空")
        return username

    def clean_password(self):
        password=self.cleaned_data["password"]
        if not password:
            raise forms.ValidationError("密码不允许为空")
        return password
