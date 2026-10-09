from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from jobs.models import Category, Job


class Command(BaseCommand):
    help = "Seeds initial industry categories and clearly labelled placeholder job vacancies for HALCON CAREER."

    def handle(self, *args, **options):
        self.stdout.write("Seeding categories...")

        categories_data = [
            ("Information Technology & Software", "it-software", "bi-laptop", "Software engineering, web development, testing, and cloud infrastructure roles."),
            ("Finance & Accounting", "finance-accounting", "bi-cash-stack", "Corporate accounting, financial planning, taxation, and auditing."),
            ("Human Resources & Staffing", "hr-recruitment", "bi-people", "Talent acquisition, HR business partnering, payroll, and people operations."),
            ("Sales & Business Development", "sales-business-dev", "bi-graph-up-arrow", "B2B sales, account management, lead generation, and client partnerships."),
            ("Customer Support & Operations", "customer-operations", "bi-headset", "Voice/chat support, technical assistance, service desk, and operations."),
            ("Healthcare & Pharmaceuticals", "healthcare-pharma", "bi-heart-pulse", "Clinical support, pharmaceutical sales, medical billing, and administrative staffing."),
            ("Engineering & Manufacturing", "engineering-manufacturing", "bi-gear", "Mechanical, electrical, production engineering, and quality assurance."),
            ("Digital Marketing & Media", "marketing-media", "bi-megaphone", "SEO, content strategy, social media management, and performance marketing."),
        ]

        created_categories = {}
        for name, slug, icon, desc in categories_data:
            cat, created = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'icon': icon, 'description': desc, 'active': True}
            )
            created_categories[slug] = cat
            status = "Created" if created else "Existing"
            self.stdout.write(f"  [{status}] Category: {name}")

        self.stdout.write("\nSeeding clearly labelled placeholder jobs...")

        sample_jobs = [
            {
                "title": "Senior Python & Django Full-Stack Developer",
                "slug": "senior-python-django-fullstack-developer",
                "category": created_categories.get("it-software"),
                "employer_name": "Confidential Client [Technology Sector]",
                "location": "Mohali, Punjab",
                "employment_type": "Full-time",
                "experience_requirements": "3-5 Years",
                "min_salary": 650000,
                "max_salary": 1000000,
                "salary_negotiable": True,
                "hide_salary": False,
                "description": "[Placeholder Vacancy] Seeking an experienced Python & Django engineer to design and scale corporate web applications and microservices for an established technology company operating out of Mohali.",
                "responsibilities": "- Develop modular, test-driven backend code in Python and Django\n- Build high-performance REST APIs for frontend integration\n- Design relational database schemas and optimize PostgreSQL queries\n- Implement security best practices (CSRF, XSS, rate limiting)",
                "required_skills": "Python, Django, PostgreSQL, REST Framework, HTML5, CSS3, JavaScript, Git",
                "qualifications": "B.Tech / B.E. / MCA in Computer Science or equivalent with 3+ years relevant experience",
                "is_featured": True,
                "is_published": True,
            },
            {
                "title": "Talent Acquisition Executive / HR Recruiter",
                "slug": "talent-acquisition-executive-hr-recruiter",
                "category": created_categories.get("hr-recruitment"),
                "employer_name": "Confidential Client [Recruitment Services]",
                "location": "Mohali, Punjab",
                "employment_type": "Full-time",
                "experience_requirements": "1-3 Years",
                "min_salary": 300000,
                "max_salary": 450000,
                "salary_negotiable": False,
                "hide_salary": False,
                "description": "[Placeholder Vacancy] Looking for a dynamic recruitment executive to manage talent sourcing, candidate screening, and client interview scheduling across Tricity hiring mandates.",
                "responsibilities": "- Source relevant candidate profiles via job boards, LinkedIn, and professional networks\n- Conduct initial phone screenings and assess candidate suitability\n- Coordinate client interview schedules and manage candidate relationship updates",
                "required_skills": "Candidate Sourcing, Resume Screening, Interview Coordination, Clear Verbal Communication",
                "qualifications": "Bachelor's degree in any field. MBA in Human Resources preferred.",
                "is_featured": True,
                "is_published": True,
            },
            {
                "title": "Corporate Accountant & Tally Specialist",
                "slug": "corporate-accountant-tally-specialist",
                "category": created_categories.get("finance-accounting"),
                "employer_name": "Confidential Client [Commercial Enterprise]",
                "location": "Chandigarh",
                "employment_type": "Full-time",
                "experience_requirements": "1-3 Years",
                "min_salary": 280000,
                "max_salary": 400000,
                "salary_negotiable": False,
                "hide_salary": False,
                "description": "[Placeholder Vacancy] Full-time accounting position handling day-to-day ledger maintenance, GST filings, TDS compliance, and bank reconciliations.",
                "responsibilities": "- Maintain computerized accounts in Tally Prime / ERP\n- Prepare monthly bank reconciliation statements\n- Assist with quarterly GST returns and TDS challan preparation\n- Maintain vendor payment vouchers and invoicing files",
                "required_skills": "Tally Prime, GST Compliance, TDS, MS Excel (VLOOKUP, Pivot), Ledger Balancing",
                "qualifications": "B.Com / M.Com / Inter-CA with practical accounting experience",
                "is_featured": True,
                "is_published": True,
            },
            {
                "title": "Customer Support Representative (Fresher Friendly)",
                "slug": "customer-support-representative-fresher-friendly",
                "category": created_categories.get("customer-operations"),
                "employer_name": "Confidential Client [Operations Hub]",
                "location": "Mohali, Punjab",
                "employment_type": "Full-time",
                "experience_requirements": "Fresher",
                "min_salary": 220000,
                "max_salary": 320000,
                "salary_negotiable": True,
                "hide_salary": False,
                "description": "[Placeholder Vacancy] Entry-level customer care role suitable for fresh graduates possessing strong interpersonal communication and active listening skills.",
                "responsibilities": "- Address customer queries and requests via inbound phone calls and email tickets\n- Maintain detailed ticket resolution logs in the CRM system\n- Adhere to quality assurance guidelines and client service standards",
                "required_skills": "Excellent English & Hindi Communication, Basic Computer Operations, Active Listening",
                "qualifications": "Graduation in any stream (Freshers welcome to apply)",
                "is_featured": False,
                "is_published": True,
            },
            {
                "title": "B2B Business Development Associate",
                "slug": "b2b-business-development-associate",
                "category": created_categories.get("sales-business-dev"),
                "employer_name": "Confidential Client [Corporate Services]",
                "location": "Mohali, Punjab",
                "employment_type": "Full-time",
                "experience_requirements": "1-3 Years",
                "min_salary": 350000,
                "max_salary": 550000,
                "salary_negotiable": True,
                "hide_salary": False,
                "description": "[Placeholder Vacancy] Seeking an ambitious business development representative to cultivate enterprise client relationships, schedule corporate presentations, and close service contracts.",
                "responsibilities": "- Identify prospective B2B clients in the northern industrial belt\n- Execute cold outreach campaigns and schedule discovery consultations\n- Present service proposals and negotiate service agreements",
                "required_skills": "B2B Sales, Lead Generation, Corporate Presentations, Negotiation, CRM Management",
                "qualifications": "Graduate / BBA / MBA with 1+ years corporate sales experience",
                "is_featured": False,
                "is_published": True,
            },
            {
                "title": "Frontend UI Engineer (React / JavaScript)",
                "slug": "frontend-ui-engineer-react-javascript",
                "category": created_categories.get("it-software"),
                "employer_name": "Confidential Client [Software Services]",
                "location": "Remote / Mohali",
                "employment_type": "Hybrid",
                "experience_requirements": "3-5 Years",
                "min_salary": 600000,
                "max_salary": 900000,
                "salary_negotiable": True,
                "hide_salary": False,
                "description": "[Placeholder Vacancy] Frontend specialist to build performant, responsive web applications with reusable design systems and clean component architectures.",
                "responsibilities": "- Implement user interface screens from design prototypes\n- Ensure seamless responsiveness across mobile and desktop breakpoints\n- Integrate RESTful APIs and state management libraries",
                "required_skills": "JavaScript (ES6+), React.js, CSS3/SCSS, Bootstrap/Tailwind, Webpack/Vite, REST APIs",
                "qualifications": "Degree in Computer Science or relevant software engineering portfolio",
                "is_featured": True,
                "is_published": True,
            },
        ]

        for job_data in sample_jobs:
            slug = job_data.pop("slug")
            job, created = Job.objects.get_or_create(slug=slug, defaults=job_data)
            status = "Created" if created else "Existing"
            self.stdout.write(f"  [{status}] Job: {job.title}")

        self.stdout.write(self.style.SUCCESS("\nSample categories and placeholder vacancies successfully initialized!"))

