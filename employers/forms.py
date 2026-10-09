from django import forms
from .models import EmployerEnquiry


class EmployerEnquiryForm(forms.ModelForm):
    # Honeypot field for anti-spam bots
    company_website_url = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = EmployerEnquiry
        fields = [
            'contact_person',
            'company_name',
            'email',
            'phone',
            'hiring_requirements',
            'vacancies_count',
            'required_skills',
            'message'
        ]
        widgets = {
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'HR Manager / Talent Acquisition Lead',
                'required': True
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company or Enterprise Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'hr@yourcompany.com',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91 9216033444',
                'required': True
            }),
            'hiring_requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe roles to hire, departments, seniority level, and locations...',
                'required': True
            }),
            'vacancies_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 500,
                'value': 1,
                'required': True
            }),
            'required_skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Key technical competencies, certifications, or educational background required...'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Target hiring timeline, CTC budget brackets, or special requirements...'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        honeypot = cleaned_data.get('company_website_url')
        if honeypot:
            raise forms.ValidationError("Spam submission detected.")
        return cleaned_data

