from django import forms

from employers.models import Company
from .models import Category, Job


class RecruiterLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'username'})
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'current-password'})
    )


class JobForm(forms.ModelForm):
    company_name = forms.CharField(
        max_length=200,
        required=False,
        label='Company name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company name'})
    )
    company_logo = forms.ImageField(
        required=False,
        label='Company logo',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Job
        fields = [
            'title', 'company', 'category', 'image', 'description', 'responsibilities',
            'required_skills', 'min_salary', 'max_salary', 'salary_period',
            'location', 'work_mode', 'employment_type', 'experience_requirements',
            'min_experience_years', 'max_experience_years', 'qualifications',
            'vacancies_count', 'application_deadline', 'application_method',
            'application_email', 'application_url', 'published_at', 'status',
            'is_featured',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'required_skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'min_salary': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'max_salary': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'salary_period': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'work_mode': forms.Select(attrs={'class': 'form-select'}),
            'employment_type': forms.Select(attrs={'class': 'form-select'}),
            'experience_requirements': forms.Select(attrs={'class': 'form-select'}),
            'min_experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.5'}),
            'max_experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.5'}),
            'qualifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'vacancies_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'application_deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'application_method': forms.Select(attrs={'class': 'form-select'}),
            'application_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'application_url': forms.URLInput(attrs={'class': 'form-control'}),
            'published_at': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].required = False
        self.fields['company'].queryset = Company.objects.order_by('name')
        self.fields['category'].queryset = Category.objects.filter(active=True).order_by('name')
        if self.instance.pk and self.instance.company_id:
            self.fields['company_name'].initial = self.instance.company.name

    def clean(self):
        cleaned_data = super().clean()
        minimum = cleaned_data.get('min_experience_years')
        maximum = cleaned_data.get('max_experience_years')
        if minimum is not None and maximum is not None and minimum > maximum:
            self.add_error('max_experience_years', 'Maximum experience must be at least the minimum experience.')
        return cleaned_data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'icon', 'active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-control'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'logo', 'website', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
