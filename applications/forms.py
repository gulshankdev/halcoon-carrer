from django import forms
from .models import JobApplication
from accounts.validators import validate_resume_file


class JobApplicationForm(forms.ModelForm):
    use_existing_resume = forms.BooleanField(
        required=False,
        initial=True,
        label="Use resume already uploaded in my candidate profile",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = JobApplication
        fields = ['full_name', 'email', 'phone', 'resume_file', 'cover_letter']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 9216033444'}),
            'resume_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.docx,.doc'}),
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Briefly describe your suitability for this vacancy or any relevant achievements...'
            }),
        }

    def __init__(self, *args, has_profile_resume=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_profile_resume = has_profile_resume

        # If candidate does not have a profile resume, resume_file is strictly required
        if not has_profile_resume:
            self.fields['use_existing_resume'].widget = forms.HiddenInput()
            self.fields['use_existing_resume'].initial = False
            self.fields['resume_file'].required = True
        else:
            self.fields['resume_file'].required = False

    def clean(self):
        cleaned_data = super().clean()
        use_existing = cleaned_data.get('use_existing_resume')
        uploaded_resume = cleaned_data.get('resume_file')

        if not use_existing and not uploaded_resume:
            self.add_error('resume_file', 'Please upload your resume document (PDF or DOCX).')

        if uploaded_resume:
            validate_resume_file(uploaded_resume)

        return cleaned_data

