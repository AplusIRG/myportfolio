// ============================================
// ROBERT SICHOMBA PORTFOLIO - MAIN JAVASCRIPT
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Portfolio initialized successfully!');
    
    // 1. Loading Spinner
    window.addEventListener('load', function() {
        setTimeout(function() {
            const spinner = document.getElementById('loading-spinner');
            if (spinner) {
                spinner.style.opacity = '0';
                setTimeout(() => spinner.style.display = 'none', 300);
            }
        }, 500);
    });
    
    // 2. Navbar Scroll Effect
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // 3. Back to Top Button
    const backToTop = document.getElementById('backToTop');
    if (backToTop) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTop.classList.add('visible');
            } else {
                backToTop.classList.remove('visible');
            }
        });
        
        backToTop.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // 4. Smooth Scrolling for Anchor Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                const navbarHeight = navbar.offsetHeight;
                const targetPosition = target.offsetTop - navbarHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // 5. Form Enhancements
    document.querySelectorAll('form').forEach(form => {
        // Add loading state to submit buttons
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            form.addEventListener('submit', function() {
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
                submitBtn.disabled = true;
            });
        }
        
        // Password toggle functionality
        form.querySelectorAll('.password-toggle').forEach(toggle => {
            toggle.addEventListener('click', function() {
                const input = this.previousElementSibling;
                if (input.type === 'password') {
                    input.type = 'text';
                    this.classList.remove('fa-eye');
                    this.classList.add('fa-eye-slash');
                } else {
                    input.type = 'password';
                    this.classList.remove('fa-eye-slash');
                    this.classList.add('fa-eye');
                }
            });
        });
    });
    
    // 6. Lazy Loading Images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img.lazy').forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // 7. Testimonial Slider
    const initTestimonialSlider = () => {
        const testimonials = document.querySelectorAll('.testimonial-card');
        if (testimonials.length > 1) {
            let currentIndex = 0;
            
            const showTestimonial = (index) => {
                testimonials.forEach((testimonial, i) => {
                    testimonial.classList.remove('active');
                    if (i === index) {
                        testimonial.classList.add('active');
                    }
                });
            };
            
            // Auto-rotate every 5 seconds
            setInterval(() => {
                currentIndex = (currentIndex + 1) % testimonials.length;
                showTestimonial(currentIndex);
            }, 5000);
            
            // Add navigation controls if needed
            const createNavigation = () => {
                const nav = document.createElement('div');
                nav.className = 'testimonial-nav';
                nav.innerHTML = `
                    <button class="testimonial-prev"><i class="fas fa-chevron-left"></i></button>
                    <button class="testimonial-next"><i class="fas fa-chevron-right"></i></button>
                `;
                
                const container = document.querySelector('.testimonial-slider');
                container.appendChild(nav);
                
                nav.querySelector('.testimonial-prev').addEventListener('click', () => {
                    currentIndex = (currentIndex - 1 + testimonials.length) % testimonials.length;
                    showTestimonial(currentIndex);
                });
                
                nav.querySelector('.testimonial-next').addEventListener('click', () => {
                    currentIndex = (currentIndex + 1) % testimonials.length;
                    showTestimonial(currentIndex);
                });
            };
            
            createNavigation();
        }
    };
    
    initTestimonialSlider();
    
    // 8. Counter Animation for Stats
    const animateCounters = () => {
        const counters = document.querySelectorAll('.counter');
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-target'));
            const increment = target / 100;
            let current = 0;
            
            const updateCounter = () => {
                if (current < target) {
                    current += increment;
                    counter.innerText = Math.floor(current);
                    setTimeout(updateCounter, 20);
                } else {
                    counter.innerText = target;
                }
            };
            
            const observer = new IntersectionObserver((entries) => {
                if (entries[0].isIntersecting) {
                    updateCounter();
                    observer.unobserve(counter);
                }
            });
            
            observer.observe(counter);
        });
    };
    
    animateCounters();
    
    // 9. Floating Elements Animation
    const floatingElements = document.querySelectorAll('.floating-element');
    floatingElements.forEach(element => {
        const randomDelay = Math.random() * 2;
        element.style.animationDelay = `${randomDelay}s`;
    });
    
    // 10. Newsletter Form Submission
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = this.querySelector('input[type="email"]').value;
            
            // Show success message
            const originalHTML = this.innerHTML;
            this.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    Thank you for subscribing! You'll hear from us soon.
                </div>
            `;
            
            // Reset form after 3 seconds
            setTimeout(() => {
                this.innerHTML = originalHTML;
                this.reset();
            }, 3000);
        });
    }
    
    // 11. Add Active Class to Current Page in Navbar
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        const linkPath = link.getAttribute('href');
        if (currentPath === linkPath || currentPath.startsWith(linkPath + '/')) {
            link.classList.add('active');
        }
    });
    
    // 12. Card Hover Effects Enhancement
    const cards = document.querySelectorAll('.service-card, .project-card, .course-card, .resource-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.zIndex = '10';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.zIndex = '1';
        });
    });
    
    // 13. Mobile Menu Improvements
    const navToggler = document.querySelector('.navbar-toggler');
    if (navToggler) {
        navToggler.addEventListener('click', function() {
            document.body.classList.toggle('menu-open');
        });
    }
    
    // 14. Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.navbar-collapse') && !e.target.closest('.navbar-toggler')) {
            const navbarCollapse = document.querySelector('.navbar-collapse.show');
            if (navbarCollapse) {
                navbarCollapse.classList.remove('show');
            }
        }
    });
    
    // 15. Parallax Effect for Hero Section
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const hero = document.querySelector('.hero-section');
        if (hero) {
            const parallaxSpeed = 0.5;
            hero.style.transform = `translateY(${scrolled * parallaxSpeed}px)`;
        }
    });
    
    // 16. Initialize AOS animations
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true,
            mirror: false,
            offset: 100
        });
    }
    
    // 17. Console Welcome Message
    console.log('%c👋 Welcome to Robert Sichomba\'s Portfolio!', 'color: #3498DB; font-size: 16px; font-weight: bold;');
    console.log('%c💻 Built with Django, Bootstrap 5, and modern web technologies.', 'color: #2C3E50;');
    console.log('%c📧 Contact: Connect with me for collaborations and projects.', 'color: #27AE60;');
});

// Add utility functions to window object
window.utils = {
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    copyToClipboard: function(text) {
        navigator.clipboard.writeText(text).then(() => {
            console.log('Text copied to clipboard');
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    }
};

// Export for module usage (if using ES6 modules)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {};
}