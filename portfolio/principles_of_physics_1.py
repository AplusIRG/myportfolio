"""
Principles of Physics 1 Course Data
Foundational physics course covering mechanics, thermodynamics, and waves
"""
from datetime import date, timedelta

def get_course_data():
    today = date.today()
    
    return {
        'title': 'Principles of Physics 1',
        'subtitle': 'Foundational Physics: Mechanics, Thermodynamics, and Wave Phenomena',
        'description': """
        A comprehensive introduction to university-level physics covering classical mechanics, 
        thermodynamics, wave motion, and optics. This course emphasizes both conceptual 
        understanding and quantitative problem-solving skills. Through interactive simulations, 
        laboratory demonstrations, and real-world applications, students will develop a deep 
        understanding of fundamental physical principles.
        
        Special attention is given to developing scientific reasoning, experimental design, 
        and mathematical modeling skills essential for advanced study in physics and 
        engineering.
        """,
        'short_description': 'Master fundamental physics principles with hands-on applications',
        'level': 'intermediate',
        'status': 'active',
        'start_date': today.isoformat(),
        'end_date': (today + timedelta(days=180)).isoformat(),
        'schedule_note': 'Two modules per week. Lab sessions every Saturday 10 AM-12 PM EST',
        'location': 'Virtual Lab + Live Demonstrations',
        'is_virtual': True,
        'prerequisites': 'High school physics and calculus. Familiarity with vectors and basic derivatives.',
        'learning_objectives': [
            'Understand and apply Newton\'s laws of motion',
            'Analyze energy conservation in mechanical systems',
            'Master principles of thermodynamics and heat transfer',
            'Understand wave phenomena and optics',
            'Develop problem-solving strategies for physics problems',
            'Apply calculus to physical systems',
            'Design and analyze simple experiments',
            'Interpret physical phenomena mathematically'
        ],
        'is_free': True,
        'price': 0.00,
        'access_level': 'enrolled',
        'modules': [
            {
                'title': 'Fundamentals: Dimensions, Units, and Vectors',
                'order': 1,
                'description': 'SI units, dimensional analysis, vector mathematics, coordinate systems',
                'date': (today + timedelta(days=7)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/physics/module1_slides.pdf',
                'video_url': 'https://youtube.com/embed/physics-module1',
                'code_url': 'https://colab.research.google.com/github/example/physics-module1',
                'estimated_duration': '90 minutes',
                'difficulty': 'beginner',
                'learning_outcomes': [
                    'Work with SI units and dimensional analysis',
                    'Perform vector operations',
                    'Use coordinate systems effectively',
                    'Apply significant figures in calculations'
                ]
            },
            {
                'title': 'Motion in One Dimension',
                'order': 2,
                'description': 'Kinematics, velocity, acceleration, constant acceleration, free fall',
                'date': (today + timedelta(days=14)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/physics/module2_slides.pdf',
                'video_url': 'https://youtube.com/embed/physics-module2',
                'estimated_duration': '120 minutes',
                'difficulty': 'beginner',
                'learning_outcomes': [
                    'Describe motion using kinematic equations',
                    'Analyze velocity and acceleration',
                    'Solve problems involving constant acceleration',
                    'Apply to free fall situations'
                ]
            },
            {
                'title': 'Motion in Two and Three Dimensions',
                'order': 3,
                'description': 'Projectile motion, circular motion, relative motion, vector kinematics',
                'date': (today + timedelta(days=21)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/physics/module3_slides.pdf',
                'video_url': 'https://youtube.com/embed/physics-module3',
                'code_url': 'https://colab.research.google.com/github/example/physics-module3',
                'estimated_duration': '150 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Analyze projectile motion',
                    'Understand circular motion',
                    'Work with relative velocity',
                    'Apply vector calculus to motion'
                ]
            },
            {
                'title': 'Force and Newton\'s Laws of Motion',
                'order': 4,
                'description': 'Newton\'s laws, forces, friction, applications to various systems',
                'date': (today + timedelta(days=28)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/physics/module4_slides.pdf',
                'video_url': 'https://youtube.com/embed/physics-module4',
                'estimated_duration': '180 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Apply Newton\'s laws to various systems',
                    'Analyze forces in equilibrium',
                    'Work with friction forces',
                    'Solve dynamics problems'
                ]
            },
            {
                'title': 'Work, Energy, and Power',
                'order': 5,
                'description': 'Work-energy theorem, conservative forces, energy conservation, power',
                'date': (today + timedelta(days=35)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/physics/module5_slides.pdf',
                'video_url': 'https://youtube.com/embed/physics-module5',
                'estimated_duration': '150 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Calculate work done by forces',
                    'Apply work-energy theorem',
                    'Understand conservative forces and potential energy',
                    'Calculate power in mechanical systems'
                ]
            },
            {
                'title': 'Linear Momentum and Collisions',
                'order': 6,
                'description': 'Momentum, impulse, conservation of momentum, elastic and inelastic collisions',
                'date': (today + timedelta(days=42)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/physics/module6_slides.pdf',
                'video_url': 'https://youtube.com/embed/physics-module6',
                'code_url': 'https://colab.research.google.com/github/example/physics-module6',
                'estimated_duration': '120 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Apply momentum conservation',
                    'Analyze different types of collisions',
                    'Work with impulse-momentum theorem',
                    'Solve rocket propulsion problems'
                ]
            },
            {
                'title': 'Rotational Motion',
                'order': 7,
                'description': 'Rotational kinematics, torque, rotational dynamics, rolling motion',
                'date': (today + timedelta(days=49)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/physics/module7_slides.pdf',
                'video_url': 'https://youtube.com/embed/physics-module7',
                'estimated_duration': '180 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Describe rotational motion',
                    'Calculate torque and rotational inertia',
                    'Apply Newton\'s laws to rotation',
                    'Analyze rolling motion'
                ]
            },
            {
                'title': 'Angular Momentum and Rotational Energy',
                'order': 8,
                'description': 'Angular momentum conservation, rotational kinetic energy, gyroscopes',
                'date': (today + timedelta(days=56)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/physics/module8_slides.pdf',
                'video_url': 'https://youtube.com/embed/physics-module8',
                'estimated_duration': '120 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Apply angular momentum conservation',
                    'Calculate rotational kinetic energy',
                    'Understand gyroscopic motion',
                    'Solve complex rotational problems'
                ]
            },
            {
                'title': 'Mechanical Properties of Matter',
                'order': 9,
                'description': 'Density, elasticity, fluids, pressure, buoyancy, fluid dynamics',
                'date': (today + timedelta(days=63)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/physics/module9_slides.pdf',
                'video_url': 'https://youtube.com/embed/physics-module9',
                'estimated_duration': '150 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Understand material properties',
                    'Apply elasticity concepts',
                    'Solve fluid statics problems',
                    'Work with Bernoulli\'s equation'
                ]
            },
            {
                'title': 'Thermal Properties and Heat Transfer',
                'order': 10,
                'description': 'Temperature, thermal expansion, ideal gases, heat transfer mechanisms',
                'date': (today + timedelta(days=70)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/physics/module10_slides.pdf',
                'video_url': 'https://youtube.com/embed/physics-module10',
                'estimated_duration': '120 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Understand temperature scales',
                    'Calculate thermal expansion',
                    'Apply ideal gas law',
                    'Analyze heat transfer mechanisms'
                ]
            },
            {
                'title': 'First Law of Thermodynamics',
                'order': 11,
                'description': 'Heat capacity, latent heat, work in thermodynamic processes, first law',
                'date': (today + timedelta(days=77)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/physics/module11_slides.pdf',
                'video_url': 'https://youtube.com/embed/physics-module11',
                'estimated_duration': '150 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Calculate heat transfer',
                    'Understand specific heat and latent heat',
                    'Apply first law of thermodynamics',
                    'Analyze thermodynamic processes'
                ]
            },
            {
                'title': 'Kinetic Theory of Gases',
                'order': 12,
                'description': 'Microscopic model of gases, molecular speeds, equipartition theorem',
                'date': (today + timedelta(days=84)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/physics/module12_slides.pdf',
                'video_url': 'https://youtube.com/embed/physics-module12',
                'code_url': 'https://colab.research.google.com/github/example/physics-module12',
                'estimated_duration': '120 minutes',
                'difficulty': 'advanced',
                'learning_outcomes': [
                    'Understand kinetic theory',
                    'Calculate molecular speeds',
                    'Apply equipartition theorem',
                    'Connect microscopic and macroscopic descriptions'
                ]
            },
            {
                'title': 'Oscillations and Simple Harmonic Motion',
                'order': 13,
                'description': 'Simple harmonic oscillators, energy in SHM, damped oscillations',
                'date': (today + timedelta(days=91)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/physics/module13_slides.pdf',
                'video_url': 'https://youtube.com/embed/physics-module13',
                'estimated_duration': '120 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Analyze simple harmonic motion',
                    'Calculate energy in oscillating systems',
                    'Understand damped oscillations',
                    'Apply to pendulum and spring systems'
                ]
            },
            {
                'title': 'Wave Motion',
                'order': 14,
                'description': 'Traveling waves, wave equation, superposition, standing waves',
                'date': (today + timedelta(days=98)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/physics/module14_slides.pdf',
                'video_url': 'https://youtube.com/embed/physics-module14',
                'estimated_duration': '150 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Describe wave properties',
                    'Understand wave equation',
                    'Apply superposition principle',
                    'Analyze standing waves'
                ]
            },
            {
                'title': 'Sound Waves',
                'order': 15,
                'description': 'Sound waves, intensity, Doppler effect, standing sound waves',
                'date': (today + timedelta(days=105)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/physics/module15_slides.pdf',
                'video_url': 'https://youtube.com/embed/physics-module15',
                'estimated_duration': '120 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Understand sound wave properties',
                    'Calculate sound intensity',
                    'Apply Doppler effect',
                    'Analyze standing sound waves'
                ]
            },
            {
                'title': 'Geometric Optics',
                'order': 16,
                'description': 'Reflection, refraction, lenses, mirrors, optical instruments',
                'date': (today + timedelta(days=112)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/physics/module16_slides.pdf',
                'video_url': 'https://youtube.com/embed/physics-module16',
                'estimated_duration': '180 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Apply laws of reflection and refraction',
                    'Analyze lens and mirror systems',
                    'Understand optical instruments',
                    'Solve geometric optics problems'
                ]
            },
            {
                'title': 'Wave Optics',
                'order': 17,
                'description': 'Interference, diffraction, polarization, optical applications',
                'date': (today + timedelta(days=119)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/physics/module17_slides.pdf',
                'video_url': 'https://youtube.com/embed/physics-module17',
                'estimated_duration': '150 minutes',
                'difficulty': 'advanced',
                'learning_outcomes': [
                    'Understand interference phenomena',
                    'Analyze diffraction patterns',
                    'Work with polarized light',
                    'Apply to modern optical devices'
                ]
            },
            {
                'title': 'Comprehensive Review and Applications',
                'order': 18,
                'description': 'Integration of concepts, complex problem solving, experimental design',
                'date': (today + timedelta(days=126)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/physics/module18_slides.pdf',
                'video_url': 'https://youtube.com/embed/physics-module18',
                'code_url': 'https://colab.research.google.com/github/example/physics-module18',
                'estimated_duration': '240 minutes',
                'difficulty': 'advanced',
                'learning_outcomes': [
                    'Integrate concepts across physics domains',
                    'Solve complex, multi-concept problems',
                    'Design and analyze experiments',
                    'Apply physics to real-world situations'
                ]
            }
        ],
        'faqs': [
            {
                'question': 'Do I need a strong math background for this course?',
                'answer': 'You should be comfortable with algebra, trigonometry, and basic calculus. We provide math reviews and support throughout the course.',
                'order': 1
            },
            {
                'question': 'Are there lab components in this virtual course?',
                'answer': 'Yes! We use virtual lab simulations, at-home experiments with common materials, and data analysis exercises. All lab equipment for virtual experiments is provided.',
                'order': 2
            },
            {
                'question': 'What software will we use for simulations?',
                'answer': 'We use PhET simulations, Python with physics libraries, and specialized physics software. All tools are free and accessible online.',
                'order': 3
            },
            {
                'question': 'How are assignments structured?',
                'answer': 'Weekly problem sets, bi-weekly lab reports, three major projects, and comprehensive exams. We emphasize both conceptual understanding and quantitative problem-solving.',
                'order': 4
            },
            {
                'question': 'Is this course suitable for engineering students?',
                'answer': 'Absolutely! This course covers the fundamental physics needed for all engineering disciplines, with special emphasis on applications to engineering problems.',
                'order': 5
            },
            {
                'question': 'What support is available for struggling students?',
                'answer': 'We offer office hours, tutoring sessions, study groups, and extensive solution guides. Our forum is actively monitored by instructors and teaching assistants.',
                'order': 6
            }
        ]
    }