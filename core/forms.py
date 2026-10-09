from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    # Honeypot field for spam prevention (must be left empty by real humans)
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ['full_name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'name@example.com',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91 98765 43210'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject of your enquiry',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Write your message here...',
                'required': True
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        honeypot = cleaned_data.get('website')
        if honeypot:
            raise forms.ValidationError("Spam submission detected.")
        return cleaned_data

