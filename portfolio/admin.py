from django.contrib import admin
from django.contrib.auth.admin import UserAdmin # Import UserAdmin for CustomUser
from .models import (
    CustomUser, Skill, Project, Testimonial, BlogPost,
    Note, Document, Book, Meeting, ContactMessage
)

# --- Custom User Admin ---
class CustomUserAdmin(UserAdmin):
    """
    Custom Admin for CustomUser model.
    Extends Django's default UserAdmin to include custom fields.
    """
    list_display = ('email', 'username', 'phone_number', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ('email', 'username', 'phone_number')
    ordering = ('email',)

    # Define the fieldsets for adding/changing users in the admin
    fieldsets = (
        (None, {'fields': ('email', 'password')}), # Use email for login
        ('Personal info', {'fields': ('username', 'phone_number', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # Define the fields that are required when adding a user via the admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'phone_number', 'password', 'password2'),
        }),
    )
    # Make email the primary field for adding users via the admin form
    model = CustomUser
    form = UserAdmin.add_form # Use UserAdmin's add form for consistency

admin.site.register(CustomUser, CustomUserAdmin)



# Portfolio Content Admin


# Skill Admin (Your existing one is already good)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'proficiency', 'icon')
    list_filter = ('proficiency',)
    search_fields = ('name', 'description')
    ordering = ('-proficiency',)

admin.site.register(Skill, SkillAdmin)


# Project Admin (Added 'is_featured' to display and list_editable)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'is_featured', 'created_at', 'updated_at')
    list_filter = ('status', 'is_featured', 'created_at', 'skills_used') # Added skills_used filter
    search_fields = ('title', 'description', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('skills_used',)
    date_hierarchy = 'created_at'
    list_editable = ('status', 'is_featured',) # Allows direct editing from list view

admin.site.register(Project, ProjectAdmin)


# Testimonial Admin (Your existing one is already good)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('author', 'role', 'is_featured', 'created_at')
    list_filter = ('is_featured', 'created_at')
    search_fields = ('author', 'role', 'content')
    list_editable = ('is_featured',)

admin.site.register(Testimonial, TestimonialAdmin)


# BlogPost Admin (Enhanced with author and access_level)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_published', 'access_level', 'created_at', 'updated_at')
    list_filter = ('category', 'is_published', 'access_level', 'created_at') # Added access_level filter
    search_fields = ('title', 'content', 'tags', 'author__username', 'author__email') # Search by author's username/email
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published', 'access_level',) # Allows direct editing from list view
    date_hierarchy = 'created_at'
    # Automatically set the author to the logged-in user when creating a new post
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj: # Only for new objects
            form.base_fields['author'].initial = request.user
            # Optionally make the author field read-only after initial setting
            # form.base_fields['author'].widget.attrs['readonly'] = 'readonly'
        return form

admin.site.register(BlogPost, BlogPostAdmin)


# Note Admin (New Model)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'access_level', 'created_at')
    list_filter = ('is_published', 'access_level', 'created_at')
    search_fields = ('title', 'content', 'author__username', 'author__email')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published', 'access_level',)
    date_hierarchy = 'created_at'
    # Similar to BlogPost, auto-set author
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields['author'].initial = request.user
        return form

admin.site.register(Note, NoteAdmin)


# Document Admin (New Model)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'owner', 'is_published', 'access_level', 'uploaded_at')
    list_filter = ('document_type', 'is_published', 'access_level', 'uploaded_at')
    search_fields = ('title', 'description', 'owner__username', 'owner__email')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published', 'access_level',)
    date_hierarchy = 'uploaded_at'
    # Auto-set owner
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields['owner'].initial = request.user
        return form

admin.site.register(Document, DocumentAdmin)


# Book Admin (New Model)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'is_featured', 'access_level', 'published_date')
    list_filter = ('genre', 'is_featured', 'access_level', 'published_date')
    search_fields = ('title', 'author', 'isbn', 'description')
    list_editable = ('is_featured', 'access_level',)
    date_hierarchy = 'published_date'
    # Auto-set recommended_by (you)
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields['recommended_by'].initial = request.user
        return form

admin.site.register(Book, BookAdmin)


# Meeting Admin (New Model)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'meeting_type', 'date', 'start_time', 'owner', 'is_active', 'requires_registration', 'num_attendees')
    list_filter = ('meeting_type', 'is_active', 'requires_registration', 'date')
    search_fields = ('title', 'description', 'owner__username', 'owner__email')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_active', 'requires_registration')
    date_hierarchy = 'date'
    filter_horizontal = ('attendees',) # For managing attendees for a meeting

    # Custom column to show number of attendees
    def num_attendees(self, obj):
        return obj.attendees.count()
    num_attendees.short_description = "Attendees"

    # Action to mark meetings as inactive
    @admin.action(description='Mark selected meetings as inactive')
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} meetings were successfully marked as inactive.')
    
    # Action to mark meetings as active
    @admin.action(description='Mark selected meetings as active')
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} meetings were successfully marked as active.')

    actions = [make_inactive, make_active]

    # Auto-set owner (you)
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields['owner'].initial = request.user
        return form

admin.site.register(Meeting, MeetingAdmin)


# ContactMessage Admin (New Model)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('name', 'email', 'subject', 'message')
    date_hierarchy = 'timestamp'
    list_editable = ('is_read',) # Allows marking as read directly from list

    # Action to mark messages as read
    @admin.action(description='Mark selected messages as read')
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} messages were successfully marked as read.')

    # Action to mark messages as unread
    @admin.action(description='Mark selected messages as unread')
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} messages were successfully marked as unread.')

    actions = [mark_as_read, mark_as_unread]

admin.site.register(ContactMessage, ContactMessageAdmin)