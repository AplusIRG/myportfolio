"""
Mathematical Methods 1 Course Data
Comprehensive mathematics course covering foundational to advanced topics
"""
from datetime import date, timedelta

def get_course_data():
    today = date.today()
    
    return {
        'title': 'Mathematical Methods 1',
        'subtitle': 'Comprehensive Mathematics from Fundamentals to Advanced Applications',
        'description': """
        A rigorous course covering essential mathematical methods required for 
        science, engineering, and advanced studies. This course systematically 
        builds from basic algebra and functions through calculus, linear algebra, 
        and probability theory. Each module includes theoretical foundations, 
        practical applications, and problem-solving techniques.
        
        Students will develop strong analytical skills, learn to model real-world 
        problems mathematically, and gain proficiency in mathematical software tools.
        """,
        'short_description': 'Master essential mathematical methods for science and engineering',
        'level': 'intermediate',
        'status': 'active',
        'start_date': today.isoformat(),
        'end_date': (today + timedelta(days=120)).isoformat(),
        'schedule_note': 'New modules released weekly. Live problem sessions every Wednesday 7-9 PM EST',
        'location': 'Virtual Classroom + Live Sessions',
        'is_virtual': True,
        'prerequisites': 'High school algebra and geometry. Basic calculus recommended but not required.',
        'learning_objectives': [
            'Master algebraic manipulation and equation solving',
            'Understand functions, graphs, and their transformations',
            'Apply trigonometric identities and solve trigonometric equations',
            'Work with complex numbers and polar coordinates',
            'Solve systems of equations using matrices',
            'Understand sequences, series, and probability theory',
            'Apply mathematical modeling to real-world problems',
            'Develop proof-writing and problem-solving skills'
        ],
        'is_free': True,
        'price': 0.00,
        'access_level': 'enrolled',
        'modules': [
            {
                'title': 'Preliminary Concepts & Real Number System',
                'order': 1,
                'description': 'Real numbers, exponents, polynomials, factoring, rational expressions, complex numbers',
                'date': (today + timedelta(days=7)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/math/module1_slides.pdf',
                'video_url': 'https://youtube.com/embed/math-module1',
                'code_url': 'https://colab.research.google.com/github/example/math1-module1',
                'estimated_duration': '90 minutes',
                'difficulty': 'beginner',
                'learning_outcomes': [
                    'Understand real number properties',
                    'Perform operations with exponents',
                    'Factor polynomials',
                    'Simplify rational expressions',
                    'Work with complex numbers'
                ],
                'additional_resources': [
                    {'title': 'Number Systems Review', 'url': '/resources/math/numbers-review.pdf', 'type': 'pdf'},
                    {'title': 'Practice Problems Set 1', 'url': '/resources/math/practice1.pdf', 'type': 'pdf'},
                    {'title': 'Complex Numbers Tutorial', 'url': 'https://example.com/complex-tutorial', 'type': 'external'}
                ]
            },
            {
                'title': 'Equations and Inequalities',
                'order': 2,
                'description': 'Linear equations, absolute value equations, quadratic equations, inequalities, variation',
                'date': (today + timedelta(days=14)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/math/module2_slides.pdf',
                'video_url': 'https://youtube.com/embed/math-module2',
                'estimated_duration': '120 minutes',
                'difficulty': 'beginner',
                'learning_outcomes': [
                    'Solve linear and absolute value equations',
                    'Solve quadratic equations using various methods',
                    'Work with rational and radical equations',
                    'Solve inequalities and represent solutions graphically'
                ]
            },
            {
                'title': 'Functions and Graphs',
                'order': 3,
                'description': 'Coordinate systems, functions, linear and quadratic functions, graph properties, regression',
                'date': (today + timedelta(days=21)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/math/module3_slides.pdf',
                'video_url': 'https://youtube.com/embed/math-module3',
                'code_url': 'https://colab.research.google.com/github/example/math1-module3',
                'estimated_duration': '150 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Understand function concepts and notation',
                    'Graph various types of functions',
                    'Analyze function properties',
                    'Perform operations on functions',
                    'Use regression to model data'
                ]
            },
            {
                'title': 'Polynomial and Rational Functions',
                'order': 4,
                'description': 'Polynomial functions, zeros, Fundamental Theorem of Algebra, rational functions',
                'date': (today + timedelta(days=28)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/math/module4_slides.pdf',
                'video_url': 'https://youtube.com/embed/math-module4',
                'estimated_duration': '120 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Apply Remainder and Factor Theorems',
                    'Analyze polynomial functions',
                    'Find zeros of polynomial functions',
                    'Graph rational functions'
                ]
            },
            {
                'title': 'Exponential and Logarithmic Functions',
                'order': 5,
                'description': 'Inverse functions, exponential functions, logarithmic functions, applications',
                'date': (today + timedelta(days=35)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/math/module5_slides.pdf',
                'video_url': 'https://youtube.com/embed/math-module5',
                'code_url': 'https://colab.research.google.com/github/example/math1-module5',
                'estimated_duration': '150 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Understand inverse functions',
                    'Work with exponential and logarithmic functions',
                    'Solve exponential and logarithmic equations',
                    'Apply to growth and decay problems'
                ]
            },
            {
                'title': 'Trigonometric Functions',
                'order': 6,
                'description': 'Angles, right triangle trigonometry, trigonometric functions, graphs, harmonic motion',
                'date': (today + timedelta(days=42)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/math/module6_slides.pdf',
                'video_url': 'https://youtube.com/embed/math-module6',
                'estimated_duration': '180 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Convert between degree and radian measure',
                    'Evaluate trigonometric functions',
                    'Graph trigonometric functions',
                    'Apply to harmonic motion'
                ]
            },
            {
                'title': 'Trigonometric Identities and Equations',
                'order': 7,
                'description': 'Trigonometric identities, sum/difference formulas, inverse trigonometric functions',
                'date': (today + timedelta(days=49)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/math/module7_slides.pdf',
                'video_url': 'https://youtube.com/embed/math-module7',
                'estimated_duration': '150 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Verify trigonometric identities',
                    'Use sum, difference, and double-angle formulas',
                    'Work with inverse trigonometric functions',
                    'Solve trigonometric equations'
                ]
            },
            {
                'title': 'Applications of Trigonometry',
                'order': 8,
                'description': 'Law of Sines and Cosines, vectors, complex numbers in trigonometric form',
                'date': (today + timedelta(days=56)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/math/module8_slides.pdf',
                'video_url': 'https://youtube.com/embed/math-module8',
                'estimated_duration': '120 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Apply Law of Sines and Cosines',
                    'Work with vectors',
                    'Use trigonometric form of complex numbers',
                    'Apply De Moivre\'s Theorem'
                ]
            },
            {
                'title': 'Systems of Equations and Inequalities',
                'order': 9,
                'description': 'Linear systems, nonlinear systems, partial fractions, linear programming',
                'date': (today + timedelta(days=63)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/math/module9_slides.pdf',
                'video_url': 'https://youtube.com/embed/math-module9',
                'code_url': 'https://colab.research.google.com/github/example/math1-module9',
                'estimated_duration': '180 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Solve systems of linear equations',
                    'Work with nonlinear systems',
                    'Perform partial fraction decomposition',
                    'Apply linear programming techniques'
                ]
            },
            {
                'title': 'Matrices and Determinants',
                'order': 10,
                'description': 'Matrix operations, inverses, determinants, Cramer\'s Rule',
                'date': (today + timedelta(days=70)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/math/module10_slides.pdf',
                'video_url': 'https://youtube.com/embed/math-module10',
                'estimated_duration': '150 minutes',
                'difficulty': 'advanced',
                'learning_outcomes': [
                    'Perform matrix operations',
                    'Find matrix inverses',
                    'Calculate determinants',
                    'Apply Cramer\'s Rule'
                ]
            },
            {
                'title': 'Sequences, Series, and Probability',
                'order': 11,
                'description': 'Sequences, arithmetic and geometric series, mathematical induction, probability',
                'date': (today + timedelta(days=77)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/math/module11_slides.pdf',
                'video_url': 'https://youtube.com/embed/math-module11',
                'estimated_duration': '180 minutes',
                'difficulty': 'advanced',
                'learning_outcomes': [
                    'Work with sequences and series',
                    'Apply mathematical induction',
                    'Use Binomial Theorem',
                    'Calculate probabilities'
                ]
            },
            {
                'title': 'Comprehensive Review and Applications',
                'order': 12,
                'description': 'Review of all concepts, advanced problem solving, mathematical modeling projects',
                'date': (today + timedelta(days=84)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/math/module12_slides.pdf',
                'video_url': 'https://youtube.com/embed/math-module12',
                'code_url': 'https://colab.research.google.com/github/example/math1-module12',
                'estimated_duration': '240 minutes',
                'difficulty': 'advanced',
                'learning_outcomes': [
                    'Integrate concepts from all modules',
                    'Solve complex, multi-step problems',
                    'Develop mathematical models',
                    'Present mathematical solutions'
                ]
            }
        ],
        'faqs': [
            {
                'question': 'What background do I need for this course?',
                'answer': 'You should be comfortable with high school algebra and geometry. Some exposure to basic calculus is helpful but not required. We\'ll review essential concepts in the first module.',
                'order': 1
            },
            {
                'question': 'How much time should I dedicate each week?',
                'answer': 'We recommend 6-8 hours per week: 2-3 hours for video lectures and readings, 2-3 hours for practice problems, and 2 hours for assignments and review.',
                'order': 2
            },
            {
                'question': 'Will there be assignments and exams?',
                'answer': 'Yes, each module includes practice problems, weekly assignments, and three major projects. There will be a midterm and final exam to assess comprehensive understanding.',
                'order': 3
            },
            {
                'question': 'What software or tools will I need?',
                'answer': 'We\'ll use Python (Jupyter Notebooks) for computational exercises, but all code will be provided. A graphing calculator or software like Desmos/GeoGebra is recommended.',
                'order': 4
            },
            {
                'question': 'Is there a certificate upon completion?',
                'answer': 'Yes, students who complete all assignments and exams with a grade of 70% or higher will receive a certificate of completion.',
                'order': 5
            },
            {
                'question': 'Can I interact with instructors and other students?',
                'answer': 'Absolutely! We have live Q&A sessions, discussion forums, and study groups. Instructors are available for office hours and forum discussions.',
                'order': 6
            }
        ]
    }