from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    CustomUser, Skill, Project, Testimonial, BlogPost,
    Note, Document, Book, Meeting, ContactMessage,
    Course, Enrollment, UserProgress, CourseModule, Lesson,
    Assignment, Submission, EmailVerification, ParentConnection,
    Certificate, CourseReview
)

# ============================================================================
# CUSTOM USER ADMIN
# ============================================================================

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'role', 'phone', 'is_staff', 'is_active', 'email_verified')
    list_filter = ('role', 'school', 'email_verified', 'is_staff', 'is_active', 'groups')
    search_fields = ('email', 'username', 'phone', 'first_name', 'last_name', 'student_id')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'first_name', 'last_name', 'phone', 'profile_picture', 'bio', 'website', 'location')}),
        ('Academic Info', {'fields': ('role', 'school', 'department', 'year_of_study', 'student_id', 'institution')}),
        ('Course Management', {'fields': ('parent_email',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at')}),
        ('Additional', {'fields': ('email_verified', 'profile_data')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'first_name', 'last_name'),
        }),
    )

    readonly_fields = ('date_joined', 'last_login', 'created_at')
    model = CustomUser

admin.site.register(CustomUser, CustomUserAdmin)


# ============================================================================
# PORTFOLIO ADMIN
# ============================================================================

class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'proficiency', 'icon')
    list_filter = ('proficiency',)
    search_fields = ('name', 'description')
    ordering = ('-proficiency',)
    filter_horizontal = ('related_courses',)   # ManyToManyField

admin.site.register(Skill, SkillAdmin)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'is_featured', 'created_at')
    list_filter = ('status', 'is_featured', 'created_at')
    search_fields = ('title', 'description', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('skills_used', 'related_courses')   # Both ManyToManyField
    date_hierarchy = 'created_at'
    list_editable = ('status', 'is_featured')

admin.site.register(Project, ProjectAdmin)


class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('author', 'role', 'is_featured', 'rating', 'created_at')
    list_filter = ('is_featured', 'rating', 'created_at')
    search_fields = ('author', 'role', 'content')
    list_editable = ('is_featured',)

admin.site.register(Testimonial, TestimonialAdmin)


class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_published', 'access_level', 'created_at', 'views')
    list_filter = ('category', 'is_published', 'access_level', 'created_at')
    search_fields = ('title', 'content', 'tags', 'author__email')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published', 'access_level')
    date_hierarchy = 'created_at'
    filter_horizontal = ('related_courses',)   # ManyToManyField

admin.site.register(BlogPost, BlogPostAdmin)


class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'course', 'is_published', 'access_level', 'created_at')
    list_filter = ('is_published', 'access_level', 'created_at', 'course')
    search_fields = ('title', 'content', 'author__email')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published', 'access_level')
    date_hierarchy = 'created_at'

admin.site.register(Note, NoteAdmin)


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'course', 'owner', 'access_level', 'download_count', 'is_published', 'uploaded_at')
    list_filter = ('document_type', 'is_published', 'access_level', 'uploaded_at', 'course')
    search_fields = ('title', 'description', 'owner__email')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published', 'access_level')   # Both must be in list_display – now access_level is included
    date_hierarchy = 'uploaded_at'
    readonly_fields = ('download_count', 'file_size')

admin.site.register(Document, DocumentAdmin)


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'is_featured', 'access_level', 'published_date')
    list_filter = ('genre', 'is_featured', 'access_level', 'published_date')
    search_fields = ('title', 'author', 'isbn', 'description')
    list_editable = ('is_featured', 'access_level')
    date_hierarchy = 'published_date'
    filter_horizontal = ('related_courses',)   # ManyToManyField

admin.site.register(Book, BookAdmin)


class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'meeting_type', 'course', 'date', 'start_time', 'owner', 'is_active', 'num_attendees')
    list_filter = ('meeting_type', 'is_active', 'date', 'course')
    search_fields = ('title', 'description', 'owner__email')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_active',)
    date_hierarchy = 'date'
    filter_horizontal = ('attendees',)   # ManyToManyField
    readonly_fields = ('created_at', 'updated_at')

    def num_attendees(self, obj):
        return obj.attendees.count()
    num_attendees.short_description = "Attendees"

    @admin.action(description='Mark selected meetings as inactive')
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} meetings were successfully marked as inactive.')
    
    @admin.action(description='Mark selected meetings as active')
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} meetings were successfully marked as active.')

    actions = [make_inactive, make_active]

admin.site.register(Meeting, MeetingAdmin)


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message_type', 'course', 'timestamp', 'is_read', 'is_responded')
    list_filter = ('is_read', 'is_responded', 'message_type', 'timestamp', 'course')
    search_fields = ('name', 'email', 'subject', 'message')
    date_hierarchy = 'timestamp'
    list_editable = ('is_read', 'is_responded')

    @admin.action(description='Mark selected messages as read')
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} messages were successfully marked as read.')

    @admin.action(description='Mark selected messages as unread')
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} messages were successfully marked as unread.')

    actions = [mark_as_read, mark_as_unread]

admin.site.register(ContactMessage, ContactMessageAdmin)


# ============================================================================
# COURSE MANAGEMENT ADMIN
# ============================================================================

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'title', 'school', 'department', 'instructor', 'enrollment_count', 'is_active', 'is_featured')
    list_filter = ('school', 'department', 'level', 'difficulty', 'is_active', 'is_featured')
    search_fields = ('course_code', 'title', 'description', 'instructor__email')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('enrollment_count', 'rating', 'views', 'created_at', 'updated_at')
    filter_horizontal = ('skills_taught', 'example_projects')   # Both ManyToManyField
    fieldsets = (
        ('Basic Information', {
            'fields': ('course_id', 'course_code', 'title', 'slug', 'description', 'detailed_description')
        }),
        ('Course Details', {
            'fields': ('school', 'department', 'instructor', 'credits', 'level', 'duration', 'difficulty')
        }),
        ('Media & Presentation', {
            'fields': ('thumbnail', 'promo_video', 'is_featured')
        }),
        ('Pricing & Enrollment', {
            'fields': ('price', 'is_free', 'is_open_for_enrollment')
        }),
        ('Statistics', {
            'fields': ('enrollment_count', 'rating', 'views')
        }),
        ('Course Structure', {
            'fields': ('prerequisites', 'learning_outcomes', 'syllabus', 'resources_structure')
        }),
        ('Portfolio Integration', {
            'fields': ('skills_taught', 'example_projects')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'created_at', 'updated_at')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at', 'status', 'progress_percentage', 'completed', 'certificate_issued')
    list_filter = ('course', 'completed', 'status', 'certificate_issued', 'enrolled_at')
    search_fields = ('user__email', 'course__title', 'certificate_id')
    readonly_fields = ('enrolled_at', 'certificate_id', 'progress_percentage')
    list_editable = ('status',)


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'chapters_completed', 'total_chapters', 'grade', 'last_accessed')
    list_filter = ('course',)
    search_fields = ('user__email', 'course__title')
    readonly_fields = ('last_accessed', 'quiz_scores', 'completed_modules', 'completed_lessons', 'completed_quizzes')
    
    def progress_percentage(self, obj):
        return f"{obj.calculate_progress():.1f}%"
    progress_percentage.short_description = "Progress"


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ('course', 'title', 'order', 'is_published')
    list_filter = ('course', 'is_published')
    search_fields = ('title', 'course__title')
    list_editable = ('order', 'is_published')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('module', 'title', 'order', 'duration_minutes', 'is_published')
    list_filter = ('module__course', 'is_published')
    search_fields = ('title', 'module__title')
    list_editable = ('order', 'is_published', 'duration_minutes')
    filter_horizontal = ('attached_documents',)   # ManyToManyField


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'assignment_type', 'due_date', 'max_points', 'created_by')
    list_filter = ('assignment_type', 'course', 'created_by')
    search_fields = ('title', 'description', 'course__title')
    # related_project is a ForeignKey, so we do NOT use filter_horizontal.
    # Instead, use raw_id_fields or just a dropdown.
    raw_id_fields = ('related_project',)   # Better for ForeignKey
    # filter_horizontal = ('related_project',)  <-- REMOVED – this caused the error


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'assignment', 'submitted_at', 'grade', 'is_graded', 'graded_by')
    list_filter = ('assignment', 'is_graded', 'submitted_at')
    search_fields = ('user__email', 'assignment__title')
    readonly_fields = ('submitted_at',)
    list_editable = ('grade', 'is_graded')


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'verification_type', 'created_at', 'is_used')
    list_filter = ('is_used', 'verification_type', 'created_at')
    search_fields = ('user__email', 'code')
    readonly_fields = ('created_at',)


@admin.register(ParentConnection)
class ParentConnectionAdmin(admin.ModelAdmin):
    list_display = ('parent', 'student', 'is_verified', 'created_at', 'can_view_grades', 'can_view_attendance', 'can_receive_notifications')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('parent__email', 'student__email')
    list_editable = ('is_verified', 'can_view_grades', 'can_view_attendance', 'can_receive_notifications')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'issued_date', 'grade', 'is_verified')
    list_filter = ('course', 'is_verified', 'issued_date')
    search_fields = ('user__email', 'course__title', 'certificate_id')
    readonly_fields = ('certificate_id', 'issued_date', 'verification_code')


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'rating', 'is_approved', 'helpful_count', 'created_at')
    list_filter = ('rating', 'is_approved', 'course')
    search_fields = ('user__email', 'course__title', 'review')
    list_editable = ('rating', 'is_approved')