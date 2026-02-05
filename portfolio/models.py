from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings # Import settings to reference AUTH_USER_MODEL
import datetime # For default date in Lecture

# Assuming you have a rich text editor integrated, like django-ckeditor or django-tinymce.
# If not, the 'content' fields will be basic text areas.
# from ckeditor.fields import RichTextField # Example if using CKEditor


class CustomUser(AbstractUser):
    """
    Custom User model to allow login with email and add a phone number.
    The username field is kept for compatibility with Django's admin,
    but email is the primary login field.
    """
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(
        _('phone number'),
        max_length=15,
        unique=True,
        blank=True, # Made blank=True to allow users to sign up without a phone number initially
        null=True # Made null=True as well
    )
    # The 'username' field is usually part of AbstractUser.
    # If you want to use it, ensure it's not removed from AbstractUser.
    # If you truly want it to be optional for your login flow, you can set it to null=True, blank=True.
    # However, since you're setting USERNAME_FIELD to 'email', 'username' will be less critical for login.
    # Let's make it optional for better user flexibility during signup.
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)

    # Set email as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    # These fields are prompted when creating a user via createsuperuser
    REQUIRED_FIELDS = ['username'] # 'phone_number' can be optional during superuser creation too if blank/null=True

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _('Custom User')
        verbose_name_plural = _('Custom Users')




### Portfolio Content Models

# These models define the core content of your portfolio.

# Skill Model
class Skill(models.Model):
    """Represents a skill with a proficiency level and an optional icon."""
    name = models.CharField(max_length=100, unique=True)
    proficiency = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Proficiency percentage (0-100)"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="FontAwesome or other icon class for visual representation (e.g., 'fa-python')"
    )
    description = models.TextField(blank=True, help_text="A brief description of the skill.")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-proficiency']
        verbose_name = _('Skill')
        verbose_name_plural = _('Skills')


# Project Model
class Project(models.Model):
    """Details about a personal project."""
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('planned', 'Planned'),
        ('archived', 'Archived'), # Added for better project lifecycle management
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, help_text="Auto-generated from title.")
    description = models.TextField(help_text="Detailed description of the project.")
    # Use RichTextField if you integrate a rich text editor
    # description = RichTextField(help_text="Detailed description of the project.")
    image = models.ImageField(upload_to='projects/', blank=True, null=True, help_text="Thumbnail or main image for the project.")
    url = models.URLField(blank=True, help_text="Link to live project demo or GitHub repository.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    skills_used = models.ManyToManyField(Skill, related_name='projects', blank=True, help_text="Skills applied in this project.")
    tags = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated tags (e.g., 'Django, Tailwind CSS, Python')."
    )
    is_featured = models.BooleanField(default=False, help_text="Check if this project should be featured on the homepage.")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')


# Testimonial Model
class Testimonial(models.Model):
    """Stores testimonials from clients or colleagues."""
    author = models.CharField(max_length=100)
    role = models.CharField(
        max_length=100,
        blank=True,
        help_text="Author's role or company (e.g., 'CEO of Example Corp')."
    )
    content = models.TextField(help_text="The actual testimonial text.")
    image = models.ImageField(
        upload_to='testimonials/',
        blank=True,
        null=True,
        help_text="Optional profile picture of the testimonial author."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(
        default=False,
        help_text="Check to display this testimonial prominently."
    )

    def __str__(self):
        return f"Testimonial by {self.author}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Testimonial')
        verbose_name_plural = _('Testimonials')




### Enhanced Blog/Notes/Media Models (for your content)

# To support HTML blogs, notes, slides, and PDFs, we'll expand the `BlogPost` and add new models.


# Blog Post Model (Enhanced)
class BlogPost(models.Model):
    """Represents a blog post, supporting rich HTML content."""
    CATEGORY_CHOICES = [
        ('web_dev', 'Web Development'),
        ('design', 'Design'),
        ('career', 'Career'),
        ('tutorial', 'Tutorial'),
        ('personal', 'Personal'), # Added a personal category
        ('tech_review', 'Technology Review'), # Added another common category
    ]
    # Use RichTextField for content if you integrate a rich text editor
    # content = RichTextField()
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, help_text="Auto-generated from title.")
    # Consider making content a RichTextField if you're using a rich text editor
    content = models.TextField(help_text="The full content of the blog post. Can contain HTML.")
    # Author field, linking to the CustomUser model
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # If a user is deleted, their posts remain but author becomes null
        null=True,
        blank=True, # Allow posts to be created without an explicit author if needed
        related_name='blog_posts',
        help_text="The author of this blog post."
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='web_dev')
    image = models.ImageField(upload_to='blog_covers/', blank=True, null=True, help_text="Main image/cover for the blog post.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False, help_text="Check to make the post publicly visible.")
    tags = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated tags for search and filtering (e.g., 'Django, Frontend, Tutorial')."
    )
    # Add a field to control access
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('registered', 'Registered Users Only'),
            ('private', 'Private (Admin Only)') # For drafts or personal notes
        ],
        default='public',
        help_text="Who can view this blog post?"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Blog Post')
        verbose_name_plural = _('Blog Posts')


# Note Model
class Note(models.Model):
    """For quick notes or short articles, potentially for registered users only."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField(help_text="The content of the note. Can contain HTML.")
    # content = RichTextField() # Use this if integrating a rich text editor
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notes',
        help_text="The author of this note."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False, help_text="Should this note be publicly visible?")
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('registered', 'Registered Users Only'),
            ('private', 'Private (Author Only)')
        ],
        default='registered',
        help_text="Who can view this note?"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Note')
        verbose_name_plural = _('Notes')


# Document (PDF/Slides) Model
class Document(models.Model):
    """For uploading and categorizing files like PDFs, slides, or other documents."""
    DOCUMENT_TYPE_CHOICES = [
        ('pdf', 'PDF Document'),
        ('slides', 'Presentation Slides'),
        ('ebook', 'E-Book'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, help_text="A brief description of the document.")
    file = models.FileField(
        upload_to='documents/',
        help_text="Upload your PDF, PPT, or other relevant document."
    )
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='pdf')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # Owner of the document, likely you as the portfolio owner
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_documents',
        help_text="The user who uploaded this document."
    )
    is_published = models.BooleanField(default=False, help_text="Check to make the document publicly downloadable.")
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('registered', 'Registered Users Only'),
            ('private', 'Private (Admin Only)')
        ],
        default='registered',
        help_text="Who can access/download this document?"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # Depending on how you want to serve files, this might link to a detail page
        # or directly to the file itself.
        return self.file.url # Direct link to the file

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')


# Book Model (for recommended books or books you've written)
class Book(models.Model):
    """Represents a book, either one you recommend or one you've written."""
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, help_text="Author(s) of the book.")
    isbn = models.CharField(max_length=13, blank=True, null=True, unique=True, help_text="International Standard Book Number (ISBN-13).")
    genre = models.CharField(max_length=100, blank=True, help_text="Genre of the book (e.g., 'Fiction', 'Non-fiction', 'Technology').")
    description = models.TextField(blank=True, help_text="A brief summary or review of the book.")
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True, help_text="Cover image of the book.")
    # Link to buy can be an affiliate link or general retail link
    purchase_link = models.URLField(blank=True, help_text="Link to purchase the book (e.g., Amazon, publisher's site).")
    recommended_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recommended_books',
        help_text="The user who recommended this book (likely yourself)."
    )
    published_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False, help_text="Check to feature this book prominently.")
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('registered', 'Registered Users Only'),
        ],
        default='public',
        help_text="Who can view this book listing?"
    )

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        ordering = ['title']
        verbose_name = _('Book')
        verbose_name_plural = _('Books')




### Meetings & Contact Models (for interactions)


# Lecture/Meeting Model (for booking short meetings)
class Meeting(models.Model):
    """
    Represents a scheduled meeting or lecture. Users can 'register' for these.
    The `owner` is you, the portfolio owner, who offers these meetings.
    """
    MEETING_TYPE_CHOICES = [
        ('1-on-1', 'One-on-One Consultation'),
        ('group_lecture', 'Group Lecture/Webinar'),
        ('discovery_call', 'Discovery Call'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200, help_text="Name or topic of the meeting/lecture.")
    slug = models.SlugField(unique=True, blank=True, help_text="Auto-generated from title.")
    description = models.TextField(help_text="Detailed agenda or description of the meeting.")
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPE_CHOICES, default='1-on-1')
    # Use timezone.now if you're working with timezones, otherwise datetime.date.today
    date = models.DateField(default=datetime.date.today, help_text="Date of the meeting.")
    start_time = models.TimeField(help_text="Start time of the meeting (e.g., 14:00).")
    end_time = models.TimeField(blank=True, null=True, help_text="End time of the meeting (optional).")
    duration_minutes = models.IntegerField(blank=True, null=True, help_text="Duration in minutes.")
    # The user who is offering the meeting (i.e., you)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, # If you delete your account, meetings might be removed
        related_name='offered_meetings',
        help_text="The user offering this meeting/lecture (likely you)."
    )
    # Link for the meeting (e.g., Zoom, Google Meet)
    meeting_link = models.URLField(blank=True, help_text="Link to the video conferencing room.")
    max_attendees = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Maximum number of participants allowed (for group lectures)."
    )
    # Users who have booked/registered for this meeting
    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='booked_meetings',
        blank=True,
        help_text="Users who have booked/registered for this meeting."
    )
    is_active = models.BooleanField(default=True, help_text="Is this meeting slot currently available for booking?")
    requires_registration = models.BooleanField(
        default=True,
        help_text="Does this meeting require users to register?"
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Optional: Price for this meeting slot (e.g., for consultations)."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} on {self.date} at {self.start_time}"

    def get_absolute_url(self):
        return reverse('meeting_detail', kwargs={'slug': self.slug})

    class Meta:
        ordering = ['date', 'start_time']
        verbose_name = _('Meeting/Lecture')
        verbose_name_plural = _('Meetings/Lectures')
        # Add a unique constraint to prevent duplicate meeting slots for the owner
        # unique_together = [['date', 'start_time', 'owner']] # Consider this if meeting slots should be unique per owner


# Contact Message Model
class ContactMessage(models.Model):
    """Stores messages submitted via the contact form."""
    name = models.CharField(max_length=100, help_text="Name of the sender.")
    email = models.EmailField(help_text="Email address of the sender.")
    subject = models.CharField(max_length=200, help_text="Subject of the message.")
    message = models.TextField(help_text="The content of the message.")
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, help_text="Mark as read once processed.")

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('Contact Message')
        verbose_name_plural = _('Contact Messages')