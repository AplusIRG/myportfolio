# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import Http404, JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
import datetime

# Import your models
from .models import (
    Project, Skill, Testimonial, BlogPost,
    Note, Document, Book, Meeting, ContactMessage,
    CustomUser, Course, CourseModule, CourseEnrollment, FAQ, Instructor, UserCourseProgress
)

# Import your forms
from .forms import SignUpForm, ContactForm
from django.contrib.auth.forms import AuthenticationForm

# --- Core Website Views (Publicly Accessible) ---

def about(request):
    """
    Renders the 'About' page. This is the initial landing page.
    """
    skills = Skill.objects.all()
    
    # Get featured courses
    featured_courses = Course.objects.filter(is_featured=True, status='active')[:3]
    
    context = {
        'linkedin_url': 'https://www.linkedin.com/in/robert-sichomba',
        'pitch_deck_url': 'https://example.com/pitch-deck',
        'contact_url': reverse('contact'),
        'skills': skills,
        'featured_courses': featured_courses,
    }
    return render(request, 'about.html', context)











def home(request):
    """
    Renders the 'Home' dashboard-like page for logged-in users,
    or redirects to 'about' if not authenticated.
    """
    if not request.user.is_authenticated:
        return redirect('about')

    # Content for logged-in users
    featured_projects = Project.objects.filter(is_featured=True, status='completed')[:3]
    latest_blog_posts = BlogPost.objects.filter(
        is_published=True,
        access_level__in=['public', 'registered']
    ).order_by('-created_at')[:3]
    
    latest_notes = Note.objects.filter(
        is_published=True,
        access_level__in=['public', 'registered'],
        author=request.user
    ).order_by('-created_at')[:3] if request.user.is_authenticated else []

    latest_documents = Document.objects.filter(
        is_published=True,
        access_level__in=['public', 'registered']
    ).order_by('-uploaded_at')[:3]

    testimonials = Testimonial.objects.filter(is_featured=True)[:3]
    
    # Get user's enrolled courses
    enrolled_courses = []
    if request.user.is_authenticated:
        enrolled_courses = CourseEnrollment.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('course')[:3]
    
    # Get featured courses - IMPORTANT: This is what your homepage uses
    featured_courses = Course.objects.filter(is_featured=True, status='active')[:3]
    
    # ===== DEBUG =====
    print("\n" + "="*60)
    print("DEBUG: HOME VIEW - FEATURED COURSES")
    print("="*60)
    print(f"User: {request.user}")
    print(f"Number of featured courses: {len(featured_courses)}")
    for i, course in enumerate(featured_courses, 1):
        print(f"{i}. {course.title}")
        print(f"   Slug: {course.slug}")
        print(f"   Featured: {course.is_featured}")
        print(f"   Status: {course.status}")
    print("="*60)
    # ===== END DEBUG =====
    
    context = {
        'featured_projects': featured_projects,
        'latest_blog_posts': latest_blog_posts,
        'latest_notes': latest_notes,
        'latest_documents': latest_documents,
        'testimonials': testimonials,
        'enrolled_courses': enrolled_courses,
        'featured_courses': featured_courses,  # This is passed to template
        'page_title': "Welcome to Your Dashboard!"
    }
    return render(request, 'home.html', context)







def contact(request):
    """
    Handles the contact form submission.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message_content = form.cleaned_data['message']

            # Save to database
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message_content
            )

            # Send email
            try:
                send_mail(
                    f"New Contact Form Submission: {subject}",
                    f"Name: {name}\nEmail: {email}\n\nMessage:\n{message_content}",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.CONTACT_EMAIL] if hasattr(settings, 'CONTACT_EMAIL') else [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                messages.success(request, 'Your message has been sent successfully! I will get back to you soon.')
            except Exception as e:
                messages.error(request, 'There was an issue sending your message. Please try again later.')
            
            return redirect('contact')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    
    context = {
        'page_title': 'Contact Me',
        'contact_email': 'sichombarobertbob@gmail.com',
        'phone_number': '+260974609823',
        'form': form
    }
    return render(request, 'contact.html', context)


def terms(request):
    """Renders the Terms and Conditions page."""
    return render(request, 'terms.html')


def privacy(request):
    """Renders the Privacy Policy page."""
    return render(request, 'privacy.html')


# --- User Authentication Views ---

def user_signup(request):
    """
    Handles user registration.
    """
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Account created successfully! Welcome.')
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()
    
    context = {
        'form': form,
        'page_title': 'Sign Up'
    }
    return render(request, 'registration/signup.html', context)


def user_login(request):
    """
    Handles user login.
    """
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username or user.email}!")
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('home')
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form,
        'page_title': 'Login'
    }
    return render(request, 'registration/login.html', context)


@login_required
def user_logout(request):
    """
    Logs out the current user.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('about')


# --- Portfolio Content Views ---

def projects_list(request):
    """
    Displays a list of all projects.
    """
    all_projects = Project.objects.all().order_by('-created_at')
    context = {
        'projects': all_projects,
        'page_title': 'My Projects'
    }
    return render(request, 'projects/projects_list.html', context)


def project_detail(request, slug):
    """
    Displays details of a single project.
    """
    project = get_object_or_404(Project, slug=slug)
    context = {
        'project': project,
        'page_title': project.title
    }
    return render(request, 'projects/project_detail.html', context)


def testimonials_list(request):
    """
    Displays a list of all testimonials.
    """
    all_testimonials = Testimonial.objects.all().order_by('-created_at')
    context = {
        'testimonials': all_testimonials,
        'page_title': 'Testimonials'
    }
    return render(request, 'testimonials/testimonials_list.html', context)


@login_required
def blog_list(request):
    """
    Displays a list of blog posts accessible to the current user.
    """
    if request.user.is_superuser or request.user.is_staff:
        blog_posts = BlogPost.objects.filter(is_published=True).order_by('-created_at')
    else:
        blog_posts = BlogPost.objects.filter(
            is_published=True,
            access_level__in=['public', 'registered']
        ).order_by('-created_at')

    context = {
        'blog_posts': blog_posts,
        'page_title': 'My Blog'
    }
    return render(request, 'blog/blog_list.html', context)


@login_required
def blog_detail(request, slug):
    """
    Displays details of a single blog post, with access control.
    """
    blog_post = get_object_or_404(BlogPost, slug=slug)

    if blog_post.access_level == 'public' and not blog_post.is_published:
        raise Http404("Blog post not found or not published.")
    elif blog_post.access_level == 'registered' and not request.user.is_authenticated:
        messages.warning(request, "Please log in to view this content.")
        return redirect(reverse('user_login') + f'?next={request.path}')
    elif blog_post.access_level == 'private' and not (request.user.is_staff or request.user.is_superuser or blog_post.author == request.user):
        messages.error(request, "You do not have permission to view this private content.")
        return redirect('home')

    context = {
        'blog_post': blog_post,
        'page_title': blog_post.title
    }
    return render(request, 'blog/blog_detail.html', context)


@login_required
def notes_list(request):
    """
    Displays a list of notes accessible to the current user.
    """
    if request.user.is_superuser or request.user.is_staff:
        notes = Note.objects.filter(is_published=True).order_by('-created_at')
    else:
        notes = Note.objects.filter(
            is_published=True,
            access_level__in=['public', 'registered']
        ).order_by('-created_at')

    context = {
        'notes': notes,
        'page_title': 'My Notes'
    }
    return render(request, 'notes/notes_list.html', context)


@login_required
def note_detail(request, slug):
    """
    Displays details of a single note, with access control.
    """
    note = get_object_or_404(Note, slug=slug)

    if note.access_level == 'public' and not note.is_published:
        raise Http404("Note not found or not published.")
    elif note.access_level == 'registered' and not request.user.is_authenticated:
        messages.warning(request, "Please log in to view this content.")
        return redirect(reverse('user_login') + f'?next={request.path}')
    elif note.access_level == 'private' and not (request.user.is_staff or request.user.is_superuser or note.author == request.user):
        messages.error(request, "You do not have permission to view this private note.")
        return redirect('home')

    context = {
        'note': note,
        'page_title': note.title
    }
    return render(request, 'notes/note_detail.html', context)


@login_required
def note_detail_by_id(request, pk):
    """Alternative note view by ID."""
    note = get_object_or_404(Note, pk=pk)
    
    # Access control
    if note.access_level == 'public' and not note.is_published:
        raise Http404("Note not found or not published.")
    elif note.access_level == 'registered' and not request.user.is_authenticated:
        messages.warning(request, "Please log in to view this content.")
        return redirect(reverse('user_login') + f'?next={request.path}')
    elif note.access_level == 'private' and not (request.user.is_staff or request.user.is_superuser or note.author == request.user):
        messages.error(request, "You do not have permission to view this private note.")
        return redirect('home')
    
    return render(request, "notes/note_detail.html", {"note": note, "page_title": note.title})


@login_required
def documents_list(request):
    """
    Displays a list of documents accessible to the current user.
    """
    if request.user.is_superuser or request.user.is_staff:
        documents = Document.objects.filter(is_published=True).order_by('-uploaded_at')
    else:
        documents = Document.objects.filter(
            is_published=True,
            access_level__in=['public', 'registered']
        ).order_by('-uploaded_at')

    context = {
        'documents': documents,
        'page_title': 'My Documents'
    }
    return render(request, 'documents/documents_list.html', context)


@login_required
def document_detail(request, slug):
    """
    Displays details of a single document, with access control.
    """
    document = get_object_or_404(Document, slug=slug)

    if document.access_level == 'public' and not document.is_published:
        raise Http404("Document not found or not published.")
    elif document.access_level == 'registered' and not request.user.is_authenticated:
        messages.warning(request, "Please log in to access this document.")
        return redirect(reverse('user_login') + f'?next={request.path}')
    elif document.access_level == 'private' and not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "You do not have permission to access this private document.")
        return redirect('home')

    context = {
        'document': document,
        'page_title': document.title
    }
    return render(request, 'documents/document_detail.html', context)


@login_required
def books_list(request):
    """
    Displays a list of books accessible to the current user.
    """
    if request.user.is_superuser or request.user.is_staff:
        books = Book.objects.all().order_by('-created_at')
    else:
        books = Book.objects.filter(access_level__in=['public', 'registered']).order_by('-created_at')

    context = {
        'books': books,
        'page_title': 'Recommended Books'
    }
    return render(request, 'books/books_list.html', context)


@login_required
def book_detail(request, pk):
    """
    Displays details of a single book, with comprehensive access control.
    """
    book = get_object_or_404(Book, pk=pk)

    if book.access_level == 'private':
        if not request.user.is_authenticated or (not request.user.is_superuser and not request.user.is_staff):
            raise Http404("Book not found or you do not have permission to access this private content.")

    if book.access_level == 'registered':
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to view details for this book.")
            return redirect(reverse('user_login') + f'?next={request.path}')

    context = {
        'book': book,
        'page_title': book.title
    }
    return render(request, 'books/book_detail.html', context)


@login_required
def meetings_list(request):
    """
    Displays a list of available meetings/lectures.
    """
    today = datetime.date.today()
    now = datetime.datetime.now().time()

    available_meetings = Meeting.objects.filter(
        is_active=True,
        date__gte=today,
    ).order_by('date', 'start_time')

    available_meetings = [
        m for m in available_meetings if m.date > today or (m.date == today and m.start_time > now)
    ]
    
    context = {
        'meetings': available_meetings,
        'page_title': 'Book a Meeting'
    }
    return render(request, 'meetings/meetings_list.html', context)


@login_required
def meeting_detail(request, slug):
    """
    Displays details of a single meeting and handles booking.
    """
    meeting = get_object_or_404(Meeting, slug=slug, is_active=True)

    if meeting.date < datetime.date.today() or (meeting.date == datetime.date.today() and meeting.start_time < datetime.datetime.now().time()):
        messages.error(request, "This meeting slot has already passed.")
        return redirect('meetings_list')

    if request.method == 'POST':
        if request.user in meeting.attendees.all():
            messages.info(request, "You are already registered for this meeting.")
            return redirect('meeting_detail', slug=slug)

        if meeting.max_attendees and meeting.attendees.count() >= meeting.max_attendees:
            messages.error(request, "This meeting is full. Please choose another slot.")
            return redirect('meetings_list')

        meeting.attendees.add(request.user)
        messages.success(request, f"You have successfully booked your spot for '{meeting.title}'!")
        return redirect('meeting_detail', slug=slug)
    
    is_attendee = request.user in meeting.attendees.all()

    context = {
        'meeting': meeting,
        'page_title': meeting.title,
        'is_attendee': is_attendee,
        'current_attendees_count': meeting.attendees.count()
    }
    return render(request, 'meetings/meeting_detail.html', context)


# --- Course Views ---

def courses_list(request):
    """
    Display list of all available courses.
    """
    courses = Course.objects.filter(
        status__in=['active', 'upcoming']
    ).order_by('-start_date')
    
    context = {
        'courses': courses,
        'page_title': 'Available Courses'
    }
    return render(request, 'courses/courses_list.html', context)


def course_detail(request, slug):
    """
    Course detail page with MIT 6.S191 style.
    """
    course = get_object_or_404(Course, slug=slug)
    
    # Get modules
    modules = CourseModule.objects.filter(course=course, is_published=True).order_by('order')
    
    # Get FAQs
    faqs = FAQ.objects.filter(course=course).order_by('order')
    
    # Get instructors
    instructors = Instructor.objects.filter(courses=course)
    
    # Check enrollment
    is_enrolled = False
    enrollment = None
    if request.user.is_authenticated:
        enrollment = CourseEnrollment.objects.filter(user=request.user, course=course).first()
        is_enrolled = enrollment is not None
    
    # Calculate progress if enrolled
    progress_percentage = 0
    if enrollment:
        progress_percentage = enrollment.get_progress_percentage()
    
    context = {
        'course': course,
        'modules': modules,
        'faqs': faqs,
        'instructors': instructors,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'progress_percentage': progress_percentage,
        'page_title': course.title
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def course_enroll(request, slug):
    """
    Enroll user in a course.
    """
    course = get_object_or_404(Course, slug=slug)
    
    # Check if already enrolled
    existing = CourseEnrollment.objects.filter(user=request.user, course=course).first()
    if existing:
        messages.info(request, f"You are already enrolled in {course.title}.")
        return redirect('course_dashboard', slug=slug)
    
    # Check if course is open for enrollment
    if course.access_level == 'enrolled' and course.status not in ['active', 'upcoming']:
        messages.error(request, "This course is not currently open for enrollment.")
        return redirect('course_detail', slug=slug)
    
    # Create enrollment
    enrollment = CourseEnrollment.objects.create(
        user=request.user,
        course=course
    )
    
    # Initialize progress
    total_modules = CourseModule.objects.filter(course=course, is_published=True).count()
    enrollment.progress_data = {
        'completed_modules': [],
        'total_modules': total_modules,
        'started_at': datetime.datetime.now().isoformat(),
        'last_module_accessed': None,
    }
    enrollment.save()
    
    # Update course enrollment count
    course.enrolled_count = CourseEnrollment.objects.filter(course=course, is_active=True).count()
    course.save()
    
    messages.success(request, f"Successfully enrolled in {course.title}!")
    return redirect('course_dashboard', slug=slug)


@login_required
def course_dashboard(request, slug):
    """
    Course learning dashboard.
    """
    course = get_object_or_404(Course, slug=slug)
    enrollment = get_object_or_404(CourseEnrollment, user=request.user, course=course)
    
    # Get modules with completion status
    modules = []
    course_modules = CourseModule.objects.filter(course=course, is_published=True).order_by('order')
    completed_modules = enrollment.progress_data.get('completed_modules', [])
    
    for module in course_modules:
        modules.append({
            'module': module,
            'is_completed': module.id in completed_modules,
            'completion_date': None  # You could store this in progress_data if needed
        })
    
    # Calculate next module
    next_module = None
    for module_data in modules:
        if not module_data['is_completed']:
            next_module = module_data['module']
            break
    
    context = {
        'course': course,
        'enrollment': enrollment,
        'modules': modules,
        'next_module': next_module,
        'progress_percentage': enrollment.get_progress_percentage(),
        'page_title': f'{course.title} - Dashboard'
    }
    return render(request, 'courses/course_dashboard.html', context)


@login_required
@require_POST
def complete_module(request, slug, module_id):
    """
    Mark module as completed.
    """
    course = get_object_or_404(Course, slug=slug)
    enrollment = get_object_or_404(CourseEnrollment, user=request.user, course=course)
    module = get_object_or_404(CourseModule, id=module_id, course=course)
    
    # Add module to completed list
    completed = enrollment.progress_data.get('completed_modules', [])
    if module_id not in completed:
        completed.append(module_id)
        enrollment.progress_data['completed_modules'] = completed
        enrollment.save()
        
        # Check if course is completed
        total = enrollment.progress_data.get('total_modules', 0)
        if len(completed) >= total:
            enrollment.completed_at = datetime.datetime.now()
            enrollment.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'progress_percentage': enrollment.get_progress_percentage(),
            'completed_count': len(completed),
            'total_count': total
        })
    
    messages.success(request, f"Marked '{module.title}' as completed!")
    return redirect('course_dashboard', slug=slug)


def course_schedule(request, slug):
    """
    Standalone schedule page.
    """
    course = get_object_or_404(Course, slug=slug)
    modules = CourseModule.objects.filter(course=course, is_published=True).order_by('order')
    
    # Check enrollment
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = CourseEnrollment.objects.filter(user=request.user, course=course).exists()
    
    context = {
        'course': course,
        'modules': modules,
        'is_enrolled': is_enrolled,
        'page_title': f'{course.title} - Schedule'
    }
    return render(request, 'courses/course_schedule.html', context)


def course_faq(request, slug):
    """
    Standalone FAQ page.
    """
    course = get_object_or_404(Course, slug=slug)
    faqs = FAQ.objects.filter(course=course).order_by('order')
    
    context = {
        'course': course,
        'faqs': faqs,
        'page_title': f'{course.title} - FAQ'
    }
    return render(request, 'courses/course_faq.html', context)


def course_team(request, slug):
    """
    Course team/instructors page.
    """
    course = get_object_or_404(Course, slug=slug)
    instructors = Instructor.objects.filter(courses=course)
    
    context = {
        'course': course,
        'instructors': instructors,
        'page_title': f'{course.title} - Team'
    }
    return render(request, 'courses/course_team.html', context)


@login_required
def my_courses(request):
    """
    User's enrolled courses.
    """
    enrollments = CourseEnrollment.objects.filter(
        user=request.user,
        is_active=True
    ).select_related('course').order_by('-enrollment_date')
    
    context = {
        'enrollments': enrollments,
        'page_title': 'My Courses'
    }
    return render(request, 'courses/my_courses.html', context)


def privacy_policy_view(request):
    """Privacy policy view."""
    return render(request, 'privacy.html', {})


def terms_of_service_view(request):
    """Terms of service view."""
    return render(request, 'terms.html', {})