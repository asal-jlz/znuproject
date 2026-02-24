from django import forms
from .models import Article
from django.contrib.auth.models import User
from .models import Payment

class SignUpForm(forms.ModelForm):
    ROLE_CHOICES = [('student', 'دانشجو'), ('professor', 'استاد')]
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="نقش کاربری")
    password = forms.CharField(widget=forms.PasswordInput(), label="رمز عبور")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"]) # رمز عبور را هش می‌کند
        if commit:
            user.save()
        return user

class ArticleUploadForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'advisor', 'file'] # فیلدهایی که دانشجو باید پر کند

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'receipt_image']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'مبلغ به ریال'}),
            'receipt_image': forms.FileInput(attrs={'class': 'w-full p-2 border rounded'}),
        }        