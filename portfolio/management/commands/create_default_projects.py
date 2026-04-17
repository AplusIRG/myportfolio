import os
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from portfolio.models import Project, Skill

class Command(BaseCommand):
    help = 'Creates default geoscience/data science projects if they do not already exist'

    def handle(self, *args, **options):
        # Define required skills with proficiency (will be created if missing)
        skill_defs = {
            'Python': 95,
            'Pandas': 90,
            'Scikit-learn': 85,
            'Matplotlib': 85,
            'Seaborn': 85,
            'GeoPandas': 80,
            'CoDaPack': 75,
            'SGeMS': 75,
            'FactorAnalyzer': 80,
            'Geostatistics': 80,
            'Compositional Data Analysis': 85,
            'Clustering': 85,
            'PCA': 85,
            'Factor Analysis': 85,
            'Variography': 80,
            'Kriging': 80,
            'Jupyter Notebooks': 90,
        }

        skill_objs = {}
        for name, prof in skill_defs.items():
            obj, created = Skill.objects.get_or_create(
                name=name,
                defaults={'proficiency': prof}
            )
            skill_objs[name] = obj
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created skill: {name}'))

        # Define projects
        projects_data = [
            {
                'title': 'Mufulira Geochemical Soil Analysis – Compositional Data & Clustering',
                'slug': 'mufulira-geochemical-soil-analysis',
                'short_description': 'Reduced 40 elements to 9 immobile elements using PCA & expert knowledge. Applied k‑means clustering on raw, clr‑transformed, and PCA‑reduced data to map stratigraphic layers in the Zambian Copperbelt.',
                'long_description': """
**Problem statement:**  
The Mufulira exploration area (Zambian Copperbelt) has 40 geochemical elements measured in soil samples. Traditional statistical methods suffer from the closure effect, and stratigraphic boundaries are not obvious from raw concentrations.

**Objective:**  
Reduce the composition to fewer than 10 meaningful elements (subcomposition) and use k‑means clustering to highlight stratigraphic layers. Compare clustering results using raw data vs. centred log‑ratio (clr) transformation.

**Methodology:**  
- Performed principal component analysis (PCA) to identify immobile elements (Al, Cr, La, Nb, Sc, Sn, Ti, V, Zr) that reflect original bedrock rather than secondary processes.  
- Applied k‑means clustering (k=3) on raw concentrations, clr‑transformed data, and PCA‑reduced scores.  
- Mapped cluster labels in 2D space to visualise spatial continuity.  
- Used robust Mahalanobis distance to detect geochemical outliers.

**Results & Interpretation:**  
- The clr‑based clustering produced spatially coherent groups that align with known stratigraphic units (footwall, ore‑host, hanging wall).  
- Outlier detection highlighted Cu‑anomalous samples associated with fault zones.  
- The 9‑element subcomposition preserved the key geochemical signal while reducing noise.

**Relevance to exploration:**  
This workflow helps exploration geologists quickly identify prospective stratigraphic horizons from surface geochemistry alone, guiding follow‑up geophysics and drilling.

**Repository:** https://github.com/RobertSichombaBob/mufulira-geochemistry
                """,
                'github_url': 'https://github.com/RobertSichombaBob/mufulira-geochemistry',
                'url': '',  # optional live demo
                'skills': ['Python', 'Pandas', 'Scikit-learn', 'Matplotlib', 'Seaborn', 'Compositional Data Analysis', 'Clustering', 'PCA'],
                'tags': 'geochemistry, clustering, compositional data analysis, k-means, exploration, zambia',
                'status': 'completed',
                'is_featured': True,
            },
            {
                'title': 'European Nutrition Patterns – Compositional Data Analysis (CoDaPack)',
                'slug': 'european-nutrition-coda',
                'short_description': 'Analysed food consumption percentages across European countries using classical statistics vs. compositional data analysis. Created variation arrays, ternary diagrams, and clr‑biplots to reveal country groupings.',
                'long_description': """
**Problem statement:**  
Nutritional data are reported as percentages of total food intake, which are compositional in nature. Classical correlation analysis can produce spurious relationships due to closure.

**Objective:**  
Compare classical EDA (correlation matrix, scatter plots) with compositional data analysis (variation array, log‑ratio biplots, ternary diagrams). Use the results to group countries by dietary habits.

**Methodology:**  
- Loaded the classic European nutrition dataset (food groups as percentages).  
- Used CoDaPack (and Python) to compute the variation array – identified log‑ratios with low variance (e.g., Fish/RedMeat) as most informative.  
- Constructed ternary diagrams for selected subcompositions (e.g., Fish, White Meat, Nuts).  
- Performed clr‑biplot to visualise relationships between food groups and country clusters.

**Results:**  
- The biplot clearly separates Mediterranean countries (high Fish, Nuts, Vegetables) from Northern European (high Meat, Dairy, Starches).  
- Eastern European countries form a distinct cluster with high Potatoes and Cereals.  
- Ternary diagrams confirmed the groupings without the need for dimension reduction.

**Key insight:**  
CoDa avoids the closure effect and reveals genuine dietary patterns that classical correlation would miss.

**Repository:** https://github.com/RobertSichombaBob/europe-nutrition-coda
                """,
                'github_url': 'https://github.com/RobertSichombaBob/europe-nutrition-coda',
                'url': '',
                'skills': ['Python', 'Pandas', 'Matplotlib', 'Seaborn', 'Compositional Data Analysis'],
                'tags': 'nutrition, compositional data analysis, biplot, europe, statistics',
                'status': 'completed',
                'is_featured': True,
            },
            {
                'title': 'Central Valley Groundwater – Cr(VI) & Redox Controls',
                'slug': 'central-valley-groundwater',
                'short_description': 'Analysed 500+ groundwater samples for Cr(VI), Fe, Mn, SO4, NO3. Used log‑ratio transforms and variation arrays to link Cr(VI) to oxic conditions. Mapped important log‑ratios and performed k‑means clustering to distinguish oxic vs. anoxic zones.',
                'long_description': """
**Problem statement:**  
Hexavalent chromium (Cr(VI)) is a groundwater contaminant of concern in California’s Central Valley. Its mobility depends on redox conditions (oxic vs. anoxic). The geochemist needed to identify which geochemical parameters control Cr(VI) enrichment.

**Objective:**  
Apply compositional data analysis to understand the relative behaviour of Cr, Fe, Mn, SO4, NO3, and other solutes. Map the spatial distribution of key log‑ratios and use clustering to define redox domains.

**Methodology:**  
- Computed variation array on 500+ samples (major ions and trace metals).  
- Identified high‑variance log‑ratios involving Cr/Mn, Cr/Fe, and NO3/SO4.  
- Plotted log‑ratio(Cr/Mn) vs. log‑ratio(NO3/SO4) – strong separation between oxic (high NO3, high Cr/Mn) and anoxic (high SO4, high Fe) samples.  
- Performed k‑means clustering on clr‑transformed data to validate redox zones.  
- Mapped cluster labels in GIS to show spatial clustering of high‑Cr(VI) areas.

**Results:**  
- High Cr(VI) is associated with high Mn and NO3 (oxic, shallow aquifers).  
- Anoxic zones show elevated Fe, SO4, and very low Cr(VI).  
- The spatial maps align with known agricultural recharge areas and groundwater flow paths.

**Value to the geochemist:**  
The log‑ratio approach provided a quantitative, unbiased way to distinguish geochemical processes, leading to better risk assessment and monitoring strategies.

**Repository:** https://github.com/RobertSichombaBob/central-valley-crvi
                """,
                'github_url': 'https://github.com/RobertSichombaBob/central-valley-crvi',
                'url': '',
                'skills': ['Python', 'Pandas', 'GeoPandas', 'Matplotlib', 'Seaborn', 'Compositional Data Analysis', 'Clustering'],
                'tags': 'groundwater, chromium, redox, geochemistry, central valley, gis',
                'status': 'completed',
                'is_featured': True,
            },
            {
                'title': 'Inner Mongolia Silver Exploration – Factor Analysis & PCA',
                'slug': 'inner-mongolia-factor-analysis',
                'short_description': 'Processed 968 soil samples (30 elements) to identify Ag‑associated geochemical factors. Performed PCA and Factor Analysis (3 vs. 4 factors), mapped factor scores, and recommended 3 drill targets based on factor anomalies aligned with NE‑trending faults.',
                'long_description': """
**Problem statement:**  
The Inner Mongolia project is a grass‑roots exploration target for silver polymetallic mineralisation. Soil samples show subtle geochemical anomalies, but the signal is obscured by background variation and multiple overprinting processes.

**Objective:**  
Use factor analysis to decompose the 30‑element dataset into latent geological/geochemical processes. Identify a factor that represents the silver‑mineralising event. Prioritise drill targets based on factor score anomalies.

**Methodology:**  
- Performed robust outlier detection (Mahalanobis distance) to flag extreme samples but kept them in the analysis.  
- Applied PCA to reduce dimensionality – scree plot suggested 4–5 components.  
- Conducted Factor Analysis with varimax rotation, testing both 3‑factor and 4‑factor models.  
- Mapped factor scores for each sample in geographic coordinates.  
- Overlaid factor score maps on the regional geology (Devonian volcaniclastics, Jurassic intrusions, NE‑trending faults).

**Results:**  
- Factor 2 (Ag‑Pb‑Zn‑Sb) explains 24% of variance and shows strong spatial correlation with mapped NE‑trending faults.  
- Factor 3 (Cu‑Au‑Bi) is associated with a different intrusive phase.  
- The 4‑factor model separated Mn‑Fe oxides (supergene) from primary sulphide signature.  
- Three high‑priority drill targets were proposed where Factor 2 scores exceed the 95th percentile and coincide with fault intersections.

**Impact:**  
The analysis reduced 30 variables to 4 interpretable factors, saving time and focusing exploration. The recommended drill holes were subsequently approved for the next field season.

**Repository:** https://github.com/RobertSichombaBob/inner-mongolia-factor-analysis
                """,
                'github_url': 'https://github.com/RobertSichombaBob/inner-mongolia-factor-analysis',
                'url': '',
                'skills': ['Python', 'Pandas', 'Scikit-learn', 'FactorAnalyzer', 'Matplotlib', 'GeoPandas', 'PCA', 'Factor Analysis'],
                'tags': 'exploration, factor analysis, pca, geochemistry, inner mongolia, silver, targeting',
                'status': 'completed',
                'is_featured': True,
            },
            {
                'title': 'Arctic Elevation Mapping – Variography & Kriging',
                'slug': 'arctic-elevation-geostatistics',
                'short_description': 'Modelled experimental variograms for regular grid and irregular flight line data (sparse & dense). Fitted spherical variograms (nugget, sill, range) and performed ordinary kriging to produce continuous elevation maps. Compared kriging quality between sparse and dense sampling.',
                'long_description': """
**Problem statement:**  
Elevation data in the Arctic are often collected along flight lines (irregularly spaced). To produce a continuous digital elevation model (DEM), interpolation is needed. Classical methods like IDW ignore spatial continuity.

**Objective:**  
Learn variogram analysis and kriging using SGeMS software. Compare experimental variograms from dense vs. sparse flight lines. Model the variogram and use it for ordinary kriging. Assess prediction uncertainty.

**Methodology:**  
- Loaded regular grid elevation map (reference) and two irregular point sets (sparse and dense flight lines).  
- Calculated experimental variograms in four directions (0°, 45°, 90°, 135°) with appropriate angle tolerances.  
- Interpreted the six parameters: nugget, sill, range in major direction, range in minor direction, azimuth, anisotropy ratio.  
- Fitted spherical variogram models manually in SGeMS.  
- Performed ordinary kriging to produce continuous elevation surfaces.  
- Compared kriging results to the true grid and to each other.

**Results:**  
- The dense flight lines produced a stable variogram with clear anisotropy (range 15 km in NE‑SW direction).  
- Sparse data produced a noisy variogram but still captured the main spatial structure.  
- Kriging from dense data reproduced the elevation map accurately (RMSE ~ 8 m); sparse data introduced smoothing but preserved major features.  
- Kriging variance maps highlighted areas of high uncertainty (far from flight lines).

**Lessons for resource estimation:**  
This exercise demonstrates how data density affects variogram reliability and kriging quality – a fundamental skill for mineral resource geologists.

**Repository:** https://github.com/RobertSichombaBob/arctic-elevation-geostatistics
                """,
                'github_url': 'https://github.com/RobertSichombaBob/arctic-elevation-geostatistics',
                'url': '',
                'skills': ['SGeMS', 'Python', 'Geostatistics', 'Variography', 'Kriging', 'Matplotlib'],
                'tags': 'geostatistics, variogram, kriging, elevation, arctic, resource estimation',
                'status': 'completed',
                'is_featured': True,
            },
        ]

        # Create each project
        for data in projects_data:
            slug = data['slug']
            # Check if project already exists
            if Project.objects.filter(slug=slug).exists():
                self.stdout.write(self.style.WARNING(f'Project "{data["title"]}" already exists, skipping.'))
                continue

            # Create project
            project = Project.objects.create(
                title=data['title'],
                slug=slug,
                description=data['short_description'],
                long_description=data['long_description'],
                github_url=data['github_url'],
                url=data.get('url', ''),
                status=data['status'],
                is_featured=data['is_featured'],
                tags=data['tags'],
            )
            # Add skills
            skill_names = data['skills']
            for skill_name in skill_names:
                if skill_name in skill_objs:
                    project.skills_used.add(skill_objs[skill_name])
            self.stdout.write(self.style.SUCCESS(f'Created project: {project.title}'))

        self.stdout.write(self.style.SUCCESS('All default projects have been processed.'))