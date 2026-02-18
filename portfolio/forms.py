# In forms.py, update the User model reference to CustomUser and adjust field names.

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

from .models import CustomUser, ContactMessage, Course, Enrollment, Submission, ParentConnection, EmailVerification

# ============================================================================
# PORTFOLIO FORMS
# ============================================================================

class SignUpForm(UserCreationForm):
    """
    Form for portfolio visitor registration.
    """
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Your Email', 'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Phone Number (Optional)', 'class': 'form-control'})
    )
    username = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Username (Optional)', 'class': 'form-control'})
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Tell us about yourself...', 'class': 'form-control', 'rows': 3}),
        required=False
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'username', 'phone', 'first_name', 'last_name', 'bio')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Last Name'})

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError(_("A user with that email already exists."))
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and CustomUser.objects.filter(phone=phone).exists():
            raise ValidationError(_("A user with that phone number already exists."))
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'visitor'
        if not user.username:
            user.username = user.email.split('@')[0]
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autofocus': True, 'placeholder': 'Your Email', 'class': 'form-control'})
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'})
    )


class ContactForm(forms.Form):
    MESSAGE_TYPE_CHOICES = [
        ('general', 'General Inquiry'),
        ('course', 'Course Inquiry'),
        ('technical', 'Technical Support'),
        ('feedback', 'Feedback'),
        ('other', 'Other'),
    ]
    
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Your Name', 'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Your Email', 'class': 'form-control'}))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'Subject', 'class': 'form-control'}))
    message_type = forms.ChoiceField(choices=MESSAGE_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Your Message', 'rows': 6, 'class': 'form-control'}))
    course = forms.ModelChoiceField(
        queryset=Course.objects.filter(is_active=True, is_open_for_enrollment=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select a course (optional)"
    )

    def save(self, user=None):
        return ContactMessage.objects.create(
            name=self.cleaned_data['name'],
            email=self.cleaned_data['email'],
            subject=self.cleaned_data['subject'],
            message=self.cleaned_data['message'],
            message_type=self.cleaned_data['message_type'],
            course=self.cleaned_data['course'],
            user=user
        )


# ============================================================================
# COURSE MANAGEMENT FORMS
# ============================================================================

class CourseRegistrationForm(UserCreationForm):
    """
    Form for course user registration (students, instructors, parents).
    """
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'your.email@institution.edu'
    }))
    full_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter your full name'
    }))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': '+260 XXX XXX XXX'
    }))
    student_id = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'University student ID'
    }))
    institution = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Your university or college'
    }))
    year_of_study = forms.ChoiceField(
        choices=[('', 'Select Year'), (1, '1st Year'), (2, '2nd Year'), (3, '3rd Year'), (4, '4th Year'), (5, '5th Year'), (6, 'Postgraduate')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    department = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Your department or major'
    }))
    school = forms.ChoiceField(
        choices=CustomUser.SCHOOL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    parent_email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'parent.email@example.com'
    }))
    role = forms.ChoiceField(
        choices=[('student', 'Student'), ('instructor', 'Instructor'), ('parent', 'Parent')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'phone', 'student_id', 'institution', 'year_of_study', 'department', 'school', 'parent_email', 'role', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Create a strong password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm your password'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('An account with this email already exists.')
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one number.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain at least one special character.')
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        name_parts = self.cleaned_data['full_name'].split()
        user.first_name = name_parts[0] if name_parts else ''
        user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        if not user.username:
            user.username = user.email.split('@')[0]
        if commit:
            user.save()
        return user


class CourseLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'your.email@institution.edu'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter your password'
    }))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not CustomUser.objects.filter(email=username).exists():
            raise ValidationError('No account found with this email address.')
        return username


class CourseEnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['course']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.filter(is_active=True, is_open_for_enrollment=True)
        self.fields['course'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        enrollment = super().save(commit=False)
        enrollment.user = self.user
        if commit:
            enrollment.save()
            enrollment.course.enrollment_count += 1
            enrollment.course.save()
        return enrollment


class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file', 'text_content']
        widgets = {
            'text_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter your submission text here...'}),
            'file': forms.FileInput(attrs={'class': 'form-control'})
        }


class ParentConnectionForm(forms.ModelForm):
    student_email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'student.email@institution.edu'
    }))

    class Meta:
        model = ParentConnection
        fields = ['student_email']

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)

    def clean_student_email(self):
        student_email = self.cleaned_data.get('student_email')
        try:
            student = CustomUser.objects.get(email=student_email, role='student')
        except CustomUser.DoesNotExist:
            raise ValidationError('No student found with this email address.')
        if ParentConnection.objects.filter(parent=self.parent, student=student).exists():
            raise ValidationError('You are already connected to this student.')
        return student_email

    def save(self, commit=True):
        connection = super().save(commit=False)
        connection.parent = self.parent
        connection.student = CustomUser.objects.get(email=self.cleaned_data['student_email'])
        if commit:
            connection.save()
        return connection


class EmailVerificationForm(forms.Form):
    code = forms.CharField(max_length=6, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter 6-digit code'
    }))


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone', 'bio', 'profile_picture', 'website', 'location']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CourseInquiryForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Your questions or comments...'}))
    preferred_contact = forms.ChoiceField(
        choices=[('email', 'Email'), ('phone', 'Phone'), ('either', 'Either')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )


# Password reset forms
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control', 'placeholder': 'Enter your email'})
    )


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control', 'placeholder': 'New Password'}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control', 'placeholder': 'Confirm New Password'}),
    )