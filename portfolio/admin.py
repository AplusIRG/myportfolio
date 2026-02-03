# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Skill, Project, Testimonial, BlogPost,
    Note, Document, Book, Meeting, ContactMessage,
    Course, CourseModule, CourseEnrollment, FAQ, Instructor, UserCourseProgress
)

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'phone_number', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ('email', 'username', 'phone_number')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'phone_number', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'phone_number', 'password1', 'password2'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)


# Portfolio Content Admin
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'proficiency', 'icon')
    list_filter = ('proficiency',)
    search_fields = ('name', 'description')
    ordering = ('-proficiency',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'is_featured', 'created_at', 'updated_at')
    list_filter = ('status', 'is_featured', 'created_at', 'skills_used')
    search_fields = ('title', 'description', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('skills_used',)
    date_hierarchy = 'created_at'
    list_editable = ('status', 'is_featured',)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('author', 'role', 'is_featured', 'created_at')
    list_filter = ('is_featured', 'created_at')
    search_fields = ('author', 'role', 'content')
    list_editable = ('is_featured',)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_published', 'access_level', 'created_at', 'updated_at')
    list_filter = ('category', 'is_published', 'access_level', 'created_at')
    search_fields = ('title', 'content', 'tags', 'author__username', 'author__email')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published', 'access_level',)
    date_hierarchy = 'created_at'


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'access_level', 'created_at')
    list_filter = ('is_published', 'access_level', 'created_at')
    search_fields = ('title', 'content', 'author__username', 'author__email')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published', 'access_level',)
    date_hierarchy = 'created_at'


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'owner', 'is_published', 'access_level', 'uploaded_at')
    list_filter = ('document_type', 'is_published', 'access_level', 'uploaded_at')
    search_fields = ('title', 'description', 'owner__username', 'owner__email')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published', 'access_level',)
    date_hierarchy = 'uploaded_at'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'is_featured', 'access_level', 'published_date')
    list_filter = ('genre', 'is_featured', 'access_level', 'published_date')
    search_fields = ('title', 'author', 'isbn', 'description')
    list_editable = ('is_featured', 'access_level',)
    date_hierarchy = 'published_date'


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'meeting_type', 'date', 'start_time', 'owner', 'is_active', 'requires_registration', 'num_attendees')
    list_filter = ('meeting_type', 'is_active', 'requires_registration', 'date')
    search_fields = ('title', 'description', 'owner__username', 'owner__email')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_active', 'requires_registration')
    date_hierarchy = 'date'
    filter_horizontal = ('attendees',)

    def num_attendees(self, obj):
        return obj.attendees.count()
    num_attendees.short_description = "Attendees"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('name', 'email', 'subject', 'message')
    date_hierarchy = 'timestamp'
    list_editable = ('is_read',)


# Course System Admin
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'status', 'start_date', 'end_date', 'enrolled_count', 'is_featured')
    list_filter = ('level', 'status', 'is_featured', 'start_date', 'access_level')
    search_fields = ('title', 'description', 'subtitle')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('meetings', 'notes', 'books', 'documents', 'projects')
    list_editable = ('status', 'is_featured', 'level')
    date_hierarchy = 'start_date'


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'is_live_session', 'date', 'is_published')
    list_filter = ('is_live_session', 'is_published', 'course')
    search_fields = ('title', 'description', 'course__title')
    list_editable = ('order', 'is_published', 'is_live_session')
    ordering = ('course', 'order')


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrollment_date', 'completed_at', 'progress_percentage', 'is_active')
    list_filter = ('course', 'is_active', 'enrollment_date', 'completed_at')
    search_fields = ('user__email', 'user__username', 'course__title')
    readonly_fields = ('enrollment_date', 'last_accessed')
    
    def progress_percentage(self, obj):
        return f"{obj.get_progress_percentage():.1f}%"
    progress_percentage.short_description = "Progress"


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('question', 'answer', 'course__title')
    list_editable = ('order',)


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_lead_instructor')
    list_filter = ('is_lead_instructor', 'role')
    search_fields = ('user__email', 'user__username', 'bio', 'role')
    filter_horizontal = ('courses',)


@admin.register(UserCourseProgress)
class UserCourseProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course_key', 'enrolled_at', 'last_accessed', 'completed_at')
    list_filter = ('course_key', 'completed_at')
    search_fields = ('user__email', 'user__username', 'course_key')
    readonly_fields = ('enrolled_at', 'last_accessed')