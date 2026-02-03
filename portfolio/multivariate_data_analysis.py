"""
Multivariate Data Analysis Course Data
Advanced statistics and data analysis course
"""
from datetime import date, timedelta

def get_course_data():
    today = date.today()
    
    return {
        'title': 'Multivariate Data Analysis',
        'subtitle': 'Advanced Statistical Methods for Complex Data Systems',
        'description': """
        An advanced course in statistical methods for analyzing complex, high-dimensional data. 
        This course covers multivariate statistical techniques including factor analysis, 
        cluster analysis, discriminant analysis, and multivariate regression. Emphasis is placed 
        on both theoretical foundations and practical applications using modern statistical 
        software.
        
        Students will work with real-world datasets from various domains including social 
        sciences, business, healthcare, and engineering. The course prepares students for 
        advanced research and data science roles requiring sophisticated analytical skills.
        """,
        'short_description': 'Master advanced multivariate statistical techniques for complex data analysis',
        'level': 'advanced',
        'status': 'active',
        'start_date': today.isoformat(),
        'end_date': (today + timedelta(days=150)).isoformat(),
        'schedule_note': 'Weekly modules with live coding sessions. Project work throughout.',
        'location': 'Virtual Classroom + Data Lab',
        'is_virtual': True,
        'prerequisites': 'Statistics 101, linear algebra, basic programming (Python/R), familiarity with hypothesis testing',
        'learning_objectives': [
            'Understand multivariate probability distributions',
            'Apply principal component analysis and factor analysis',
            'Perform cluster analysis and discriminant analysis',
            'Build and interpret multivariate regression models',
            'Implement canonical correlation analysis',
            'Work with multivariate analysis of variance (MANOVA)',
            'Visualize high-dimensional data effectively',
            'Apply multivariate techniques to real-world problems'
        ],
        'is_free': False,
        'price': 199.00,
        'access_level': 'enrolled',
        'modules': [
            {
                'title': 'Introduction to Multivariate Analysis',
                'order': 1,
                'description': 'Multivariate data concepts, visualization techniques, software tools',
                'date': (today + timedelta(days=7)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/data/module1_slides.pdf',
                'video_url': 'https://youtube.com/embed/data-module1',
                'code_url': 'https://colab.research.google.com/github/example/data-module1',
                'estimated_duration': '90 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Understand multivariate data structures',
                    'Visualize multivariate data',
                    'Set up analysis environment',
                    'Load and explore multivariate datasets'
                ],
                'additional_resources': [
                    {'title': 'Multivariate Data Primer', 'url': '/resources/data/multivariate-primer.pdf', 'type': 'pdf'},
                    {'title': 'Python/R Setup Guide', 'url': '/resources/data/setup-guide.pdf', 'type': 'pdf'},
                    {'title': 'Sample Datasets', 'url': '/resources/data/sample-datasets.zip', 'type': 'data'}
                ]
            },
            {
                'title': 'Multivariate Probability Distributions',
                'order': 2,
                'description': 'Multivariate normal distribution, covariance matrices, marginal and conditional distributions',
                'date': (today + timedelta(days=14)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/data/module2_slides.pdf',
                'video_url': 'https://youtube.com/embed/data-module2',
                'code_url': 'https://colab.research.google.com/github/example/data-module2',
                'estimated_duration': '120 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Understand multivariate normal distribution',
                    'Work with covariance matrices',
                    'Calculate marginal and conditional distributions',
                    'Simulate multivariate data'
                ]
            },
            {
                'title': 'Principal Component Analysis (PCA)',
                'order': 3,
                'description': 'PCA theory, implementation, interpretation, applications to dimension reduction',
                'date': (today + timedelta(days=21)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/data/module3_slides.pdf',
                'video_url': 'https://youtube.com/embed/data-module3',
                'code_url': 'https://colab.research.google.com/github/example/data-module3',
                'estimated_duration': '150 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Understand PCA mathematical foundations',
                    'Implement PCA in software',
                    'Interpret PCA results',
                    'Apply PCA for dimension reduction'
                ]
            },
            {
                'title': 'Factor Analysis',
                'order': 4,
                'description': 'Factor analysis models, rotation methods, factor interpretation, applications',
                'date': (today + timedelta(days=28)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/data/module4_slides.pdf',
                'video_url': 'https://youtube.com/embed/data-module4',
                'estimated_duration': '180 minutes',
                'difficulty': 'advanced',
                'learning_outcomes': [
                    'Understand factor analysis models',
                    'Apply rotation methods',
                    'Interpret factor loadings',
                    'Compare PCA and factor analysis'
                ]
            },
            {
                'title': 'Multidimensional Scaling (MDS)',
                'order': 5,
                'description': 'MDS algorithms, distance metrics, visualization, applications',
                'date': (today + timedelta(days=35)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/data/module5_slides.pdf',
                'video_url': 'https://youtube.com/embed/data-module5',
                'code_url': 'https://colab.research.google.com/github/example/data-module5',
                'estimated_duration': '120 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Understand MDS concepts',
                    'Work with different distance metrics',
                    'Implement MDS algorithms',
                    'Visualize MDS results'
                ]
            },
            {
                'title': 'Cluster Analysis: Hierarchical Methods',
                'order': 6,
                'description': 'Hierarchical clustering, linkage methods, dendrogram interpretation',
                'date': (today + timedelta(days=42)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/data/module6_slides.pdf',
                'video_url': 'https://youtube.com/embed/data-module6',
                'estimated_duration': '150 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Implement hierarchical clustering',
                    'Understand different linkage methods',
                    'Interpret dendrograms',
                    'Determine optimal number of clusters'
                ]
            },
            {
                'title': 'Cluster Analysis: Partitioning Methods',
                'order': 7,
                'description': 'K-means clustering, model-based clustering, cluster validation',
                'date': (today + timedelta(days=49)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/data/module7_slides.pdf',
                'video_url': 'https://youtube.com/embed/data-module7',
                'code_url': 'https://colab.research.google.com/github/example/data-module7',
                'estimated_duration': '120 minutes',
                'difficulty': 'intermediate',
                'learning_outcomes': [
                    'Implement K-means clustering',
                    'Understand model-based clustering',
                    'Validate clustering results',
                    'Compare clustering methods'
                ]
            },
            {
                'title': 'Discriminant Analysis',
                'order': 8,
                'description': 'Linear discriminant analysis, quadratic discriminant analysis, classification',
                'date': (today + timedelta(days=56)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/data/module8_slides.pdf',
                'video_url': 'https://youtube.com/embed/data-module8',
                'estimated_duration': '180 minutes',
                'difficulty': 'advanced',
                'learning_outcomes': [
                    'Understand discriminant analysis theory',
                    'Implement LDA and QDA',
                    'Evaluate classification performance',
                    'Apply to real classification problems'
                ]
            },
            {
                'title': 'Canonical Correlation Analysis',
                'order': 9,
                'description': 'CCA theory, implementation, interpretation, applications to correlated datasets',
                'date': (today + timedelta(days=63)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/data/module9_slides.pdf',
                'video_url': 'https://youtube.com/embed/data-module9',
                'code_url': 'https://colab.research.google.com/github/example/data-module9',
                'estimated_duration': '150 minutes',
                'difficulty': 'advanced',
                'learning_outcomes': [
                    'Understand CCA mathematical foundations',
                    'Implement CCA',
                    'Interpret canonical correlations',
                    'Apply CCA to multivariate datasets'
                ]
            },
            {
                'title': 'Multivariate Analysis of Variance (MANOVA)',
                'order': 10,
                'description': 'MANOVA models, test statistics, assumptions, post-hoc analysis',
                'date': (today + timedelta(days=70)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/data/module10_slides.pdf',
                'video_url': 'https://youtube.com/embed/data-module10',
                'estimated_duration': '120 minutes',
                'difficulty': 'advanced',
                'learning_outcomes': [
                    'Understand MANOVA concepts',
                    'Implement MANOVA models',
                    'Interpret MANOVA results',
                    'Perform post-hoc analysis'
                ]
            },
            {
                'title': 'Multivariate Regression Analysis',
                'order': 11,
                'description': 'Multivariate linear regression, model selection, diagnostics, interpretation',
                'date': (today + timedelta(days=77)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/data/module11_slides.pdf',
                'video_url': 'https://youtube.com/embed/data-module11',
                'code_url': 'https://colab.research.google.com/github/example/data-module11',
                'estimated_duration': '180 minutes',
                'difficulty': 'advanced',
                'learning_outcomes': [
                    'Build multivariate regression models',
                    'Select appropriate models',
                    'Diagnose model assumptions',
                    'Interpret multivariate regression results'
                ]
            },
            {
                'title': 'Structural Equation Modeling (SEM)',
                'order': 12,
                'description': 'SEM fundamentals, path analysis, confirmatory factor analysis, model fit',
                'date': (today + timedelta(days=84)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/data/module12_slides.pdf',
                'video_url': 'https://youtube.com/embed/data-module12',
                'estimated_duration': '240 minutes',
                'difficulty': 'advanced',
                'learning_outcomes': [
                    'Understand SEM concepts',
                    'Specify SEM models',
                    'Estimate and test SEM models',
                    'Interpret SEM results'
                ]
            },
            {
                'title': 'Time Series Multivariate Analysis',
                'order': 13,
                'description': 'Multivariate time series, VAR models, cointegration, forecasting',
                'date': (today + timedelta(days=91)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/data/module13_slides.pdf',
                'video_url': 'https://youtube.com/embed/data-module13',
                'code_url': 'https://colab.research.google.com/github/example/data-module13',
                'estimated_duration': '180 minutes',
                'difficulty': 'advanced',
                'learning_outcomes': [
                    'Analyze multivariate time series',
                    'Build VAR models',
                    'Test for cointegration',
                    'Forecast multivariate time series'
                ]
            },
            {
                'title': 'Bayesian Multivariate Methods',
                'order': 14,
                'description': 'Bayesian approaches to multivariate analysis, MCMC methods, applications',
                'date': (today + timedelta(days=98)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/data/module14_slides.pdf',
                'video_url': 'https://youtube.com/embed/data-module14',
                'estimated_duration': '150 minutes',
                'difficulty': 'advanced',
                'learning_outcomes': [
                    'Understand Bayesian multivariate methods',
                    'Implement MCMC for multivariate models',
                    'Compare frequentist and Bayesian approaches',
                    'Apply Bayesian methods to complex data'
                ]
            },
            {
                'title': 'Machine Learning Extensions',
                'order': 15,
                'description': 'Multivariate methods in ML, neural networks for multivariate data, deep learning approaches',
                'date': (today + timedelta(days=105)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/data/module15_slides.pdf',
                'video_url': 'https://youtube.com/embed/data-module15',
                'code_url': 'https://colab.research.google.com/github/example/data-module15',
                'estimated_duration': '180 minutes',
                'difficulty': 'advanced',
                'learning_outcomes': [
                    'Connect multivariate statistics to ML',
                    'Apply neural networks to multivariate data',
                    'Understand deep learning for high-dimensional data',
                    'Compare statistical and ML approaches'
                ]
            },
            {
                'title': 'Capstone Project and Applications',
                'order': 16,
                'description': 'Comprehensive project integrating all techniques, real-world applications, presentation skills',
                'date': (today + timedelta(days=112)).isoformat(),
                'is_live_session': True,
                'slides_url': '/static/courses/data/module16_slides.pdf',
                'video_url': 'https://youtube.com/embed/data-module16',
                'estimated_duration': '300 minutes',
                'difficulty': 'advanced',
                'learning_outcomes': [
                    'Integrate multiple multivariate techniques',
                    'Apply methods to complex real-world problems',
                    'Present analytical results effectively',
                    'Develop complete analytical workflows'
                ]
            }
        ],
        'faqs': [
            {
                'question': 'What programming languages are used in this course?',
                'answer': 'We primarily use Python with pandas, NumPy, SciPy, and scikit-learn. R code examples are also provided. Students can choose their preferred language for assignments.',
                'order': 1
            },
            {
                'question': 'How much math background do I need?',
                'answer': 'You should be comfortable with linear algebra (matrices, eigenvectors), calculus (multivariable), and probability theory. We review essential concepts but assume familiarity.',
                'order': 2
            },
            {
                'question': 'Are there real datasets to work with?',
                'answer': 'Yes! We use datasets from various domains including finance, healthcare, social sciences, and engineering. All datasets are provided with detailed documentation.',
                'order': 3
            },
            {
                'question': 'What software will I need?',
                'answer': 'Python/R with appropriate libraries, Jupyter Notebooks, and optionally specialized software like RStudio. All software is free and open-source.',
                'order': 4
            },
            {
                'question': 'Is this course suitable for PhD research?',
                'answer': 'Absolutely. The course covers advanced methods used in academic research across many disciplines. Many PhD students use these techniques in their dissertations.',
                'order': 5
            },
            {
                'question': 'What kind of projects will we complete?',
                'answer': 'You\'ll complete three mini-projects applying specific techniques and one comprehensive capstone project analyzing a complex, real-world dataset from start to finish.',
                'order': 6
            }
        ]
    }