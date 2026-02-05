from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, ContactMessage # Import ContactMessage for the contact form

class SignUpForm(UserCreationForm):
    """
    Custom form for user registration using CustomUser model.
    Inherits from UserCreationForm for secure password handling.
    """
    # Override email and phone_number to make them truly unique and provide better feedback
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text=_('Required. Enter a valid email address.'),
        widget=forms.EmailInput(attrs={'placeholder': 'Your Email'})
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False, # Set to False as per models.py update if you want it optional
        help_text=_('Enter your phone number.'),
        widget=forms.TextInput(attrs={'placeholder': 'Phone Number (Optional)'})
    )
    # The 'username' field from UserCreationForm.
    # If you want it optional, you set it in the CustomUser model.
    # Here, we can add a placeholder for better UX.
    username = forms.CharField(
        max_length=150,
        required=False, # Set to False as per models.py update if you want it optional
        help_text=_('Choose a unique username.'),
        widget=forms.TextInput(attrs={'placeholder': 'Username (Optional)'})
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # Ensure fields here match what you want users to fill out during signup.
        # 'password1' and 'password2' are implicitly handled by UserCreationForm.
        fields = ('email', 'username', 'phone_number',) # Removed password1/2 from explicit fields

    # You don't usually need to override save() for UserCreationForm
    # unless you have very specific logic, as it handles user creation well.
    # The default save() will correctly map to your CustomUser fields.
    # If phone_number is truly unique and required, you can add a clean method for it.
    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError(_("A user with that email already exists."))
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and CustomUser.objects.filter(phone_number=phone_number).exists():
            raise ValidationError(_("A user with that phone number already exists."))
        return phone_number

    # No need to override save() unless you have custom, complex logic
    # The default save() of UserCreationForm works fine with CustomUser
    # as long as the fields are correctly defined in Meta.

class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form to ensure email is used for login.
    """
    username = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autofocus': True, 'placeholder': 'Your Email'})
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        # Ensure 'username' field maps to 'email' for authentication backend
        self.fields['username'].widget.attrs['name'] = 'email' # For template rendering if needed

    # The clean method from AuthenticationForm is designed to work with
    # USERNAME_FIELD on the User model. Since CustomUser.USERNAME_FIELD is 'email',
    # this form will correctly authenticate against the email field.


class CustomPasswordResetForm(PasswordResetForm):
    """
    Custom form for password reset.
    """
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'placeholder': 'Enter your email'})
    )

class CustomSetPasswordForm(SetPasswordForm):
    """
    Custom form for setting a new password.
    """
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'placeholder': 'New Password'}),
        strip=False,
        help_text=_("<ul><li>Your password can't be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can't be a commonly used password.</li><li>Your password can't be entirely numeric.</li></ul>"),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'placeholder': 'Confirm New Password'}),
    )


class ContactForm(forms.Form):
    """
    Form for users to send messages via the contact page.
    """
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Your Name', 'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Your Email', 'class': 'form-control'})
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Subject', 'class': 'form-control'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Your Message', 'rows': 6, 'class': 'form-control'})
    )

    def save(self):
        """
        Saves the contact message to the database.
        """
        return ContactMessage.objects.create(
            name=self.cleaned_data['name'],
            email=self.cleaned_data['email'],
            subject=self.cleaned_data['subject'],
            message=self.cleaned_data['message']
        )