# HALCON CAREER — Production Recruitment Consultancy Platform

> **Tagline:** Connecting Talent. Creating Opportunities.  
> **Headquarters:** SCO 12–13, 2nd Floor, Phase 11, Mohali, Punjab – 160065  
> **Contact Numbers:** +91 9216033444 | +91 8699000984  
> **Official Email:** contact@halconcareer.com  

---

## 1. Executive Summary & Brand Positioning

**HALCON CAREER** is a full-stack, enterprise-grade recruitment and staffing consultancy web platform built with Python and Django. The platform bridges the gap between ambitious job seekers and forward-thinking corporate employers across technology, commercial, and operational domains.

The design system adheres to a modern, corporate aesthetic using a premium deep navy (`#142B4A`) and teal (`#0F9D95`) palette, clean sans-serif typography (Inter), responsive Bootstrap 5 components, and privacy-first resume handling.

---

## 2. System Architecture & Modular Django Applications

The codebase follows high-cohesion, low-coupling design principles divided into five modular Django applications:

| Application | Primary Purpose & Features |
| :--- | :--- |
| **`core`** | Corporate homepage, About Us, Services catalog, Contact Us with spam protection, Legal pages (Privacy Policy, Terms of Service, Candidate Consent Policy), Health Check endpoint (`/health/`), dynamic `robots.txt`, XML sitemap (`/sitemap.xml`), and custom 400/403/404/500 error handlers. |
| **`accounts`** | Candidate account registration, session authentication, password management, profile management (education, skills, experience summary), and permission-controlled resume downloads. |
| **`jobs`** | Vacancy catalog, slug-based URLs, keyword search, multi-parameter filtering (category, location, job type, experience), salary formatting, and pagination. |
| **`applications`** | Candidate job application submission, profile resume reuse, duplicate application prevention, application review statuses, and secure candidate dashboards. |
| **`employers`** | B2B employer hiring mandate intake form, vacancy specifications, server-side validation, anti-spam honeypot, and management dashboard. |

---

## 3. Technology Stack

- **Backend:** Python (>= 3.11), Django 5.x/6.x, Django REST Framework
- **Database:** PostgreSQL for production (managed via `dj-database-url`), SQLite for local development
- **Static Assets:** WhiteNoise with compressed manifest caching
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons, Google Fonts (Inter)
- **Security & Configuration:** `python-decouple`, CSRF protection, secure cookie flags, honeypot spam protection, role-based resume access control
- **WSGI Server:** Gunicorn (for production Linux containers)

---

## 4. UI/UX Design System Specification

- **Primary Deep Navy:** `#142B4A` (Headers, brand elements, hero background)
- **Deep Navy Dark:** `#0D1C30` (Footer, top announcement bar)
- **Accent Teal:** `#0F9D95` (Primary action buttons, highlights, badges)
- **Accent Teal Hover:** `#0C827B`
- **Soft Teal Highlight:** `#E8F7F6`
- **Light Background:** `#F5F7FA`
- **Body Text:** `#344054`
- **Border Neutral:** `#E4E7EC`
- **Typography:** `Inter`, sans-serif
- **Layout:** Generous whitespace, clean card grids, accessible color contrast ratios (WCAG AA compliant).

---

## 5. Local Development Setup Guide

### Prerequisites
- Python 3.11, 3.12, 3.13, or 3.14 installed
- Git installed

### Step-by-Step Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-organization/halcon-career.git
   cd halcon-career
   ```

2. **Create and activate a Python virtual environment:**
   - **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Copy `.env.example` to `.env`:
   - **Windows (PowerShell):**
     ```powershell
     Copy-Item .env.example .env
     ```
   - **Linux / macOS:**
     ```bash
     cp .env.example .env
     ```

5. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Seed industry categories and initial placeholder vacancies:**
   ```bash
   python manage.py seed_sample_data
   ```

7. **Create the administrator superuser:**
   ```bash
   python manage.py create_admin
   ```
   *Default generated credentials:*
   - **Username:** `admin`
   - **Password:** `Admin@Halcon2026`
   *(You can modify credentials in Django admin or via `--username` and `--password` flags).*

8. **Collect static assets:**
   ```bash
   python manage.py collectstatic --no-input
   ```

9. **Start the local development server:**
   ```bash
   python manage.py runserver
   ```
   Open your browser at `http://127.0.0.1:8000/`.

---

## 6. Automated Testing

The project includes unit and integration tests across all five applications:
- Public pages and context processors
- Candidate registration, login, logout, and profile updates
- Vacancy search and multi-field filtering
- Published vs. unpublished draft status visibility
- Job application submission and duplicate prevention
- File extension and size validation (PDF/DOCX, max 5MB)
- Permission-gated resume downloads
- Employer enquiry form validation and honeypot spam protection

### Run Tests:
```bash
python manage.py test
```

### Run Tests with Verbosity:
```bash
python manage.py test -v 2
```

---

## 7. Security Architecture & Private Resume Protection

### Strict Resume Access Control
Uploaded resumes contain sensitive candidate PII (Personally Identifiable Information). In HALCON CAREER:
1. Resumes are **never** exposed through guessable public URLs.
2. Resume downloads are routed through dedicated authenticated endpoints:
   - Profile resumes: `/accounts/profile/resume/<user_id>/`
   - Application resumes: `/applications/resume/<application_id>/`
3. Each request enforces authorization checks:
   ```python
   if not (request.user.is_staff or request.user == application.candidate):
       raise PermissionDenied("You do not have permission to access this candidate resume.")
   ```
4. Search engine crawlers are explicitly disallowed from indexing resume paths in `robots.txt`.

### Production Security Headers
When `DEBUG=False` in `.env`:
- `SECURE_SSL_REDIRECT = True` (forces HTTPS)
- `SESSION_COOKIE_SECURE = True`
- `CSRF_COOKIE_SECURE = True`
- `SECURE_BROWSER_XSS_FILTER = True`
- `SECURE_CONTENT_TYPE_NOSNIFF = True`
- `X_FRAME_OPTIONS = 'DENY'` (clickjacking prevention)
- `SECURE_HSTS_SECONDS = 31536000` (HTTP Strict Transport Security)

---

## 8. Django Admin Features

Access the admin dashboard at `http://127.0.0.1:8000/admin/`:
- **Job Vacancies Management:** Filter by category, location, and employment type. Publish, unpublish, or feature vacancies in bulk.
- **Job Applications Review:** Filter by review status (`Submitted`, `Under Review`, `Shortlisted`, `Interview`, `Selected`, `Rejected`). Update candidate statuses directly from the list view.
- **Export to CSV:** Authorized recruiters can export candidate applications and employer enquiries to CSV with a single click.
- **Secure Resume Links:** Recruiters can download submitted candidate resumes directly from the admin panel.
- **Employer Enquiries:** Track corporate staffing mandates and update status from `New` to `Contacted`, `In Discussion`, or `Closed`.

---

## 9. Production Deployment Guide (Render / Railway / Cloud)

### Deployment to Render

1. **Push your code to a GitHub repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial production release of HALCON CAREER"
   git branch -M main
   git remote add origin https://github.com/<your-username>/halcon-career.git
   git push -u origin main
   ```

2. **Create a PostgreSQL Database on Render:**
   - Log in to [Render.com](https://render.com/).
   - Click **New +** -> **PostgreSQL**.
   - Name: `halcon-career-db`.
   - Copy the **Internal Database URL**.

3. **Create a Web Service on Render:**
   - Click **New +** -> **Web Service**.
   - Connect your GitHub repository `halcon-career`.
   - **Environment:** `Python 3`
   - **Build Command:**
     ```bash
     pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --no-input
     ```
   - **Start Command:**
     ```bash
     gunicorn config.wsgi:application
     ```

4. **Set Environment Variables in Render Dashboard:**
   - `DEBUG`: `False`
   - `SECRET_KEY`: `<Generate a secure 50+ character random string>`
   - `ALLOWED_HOSTS`: `your-service-name.onrender.com,halconcareer.com,www.halconcareer.com`
   - `DATABASE_URL`: `<Paste your Render PostgreSQL connection string>`
   - `SECURE_SSL_REDIRECT`: `True`
   - `SESSION_COOKIE_SECURE`: `True`
   - `CSRF_COOKIE_SECURE`: `True`

5. **Initial Data Seeding on Production:**
   - Go to your Web Service in Render -> **Shell** tab:
     ```bash
     python manage.py seed_sample_data
     python manage.py create_admin --password 'YourStrongProdPassword!'
     ```

### Production Media Storage Recommendation
> **Important Note on Uploaded Resumes:**  
> Ephemeral cloud containers (such as Render free tiers or Heroku dynos) reset their local disk upon redeployment. While WhiteNoise permanently manages static assets (CSS, JS, logos), user-uploaded media (candidate resumes) requires persistent storage in production.  
> **Recommended Solution:** Connect **AWS S3** or **Google Cloud Storage** using `django-storages` with private ACLs (`default_acl = 'private'`), or attach a Render Persistent Disk mounted to `/media/`.

---

## 10. Connecting a Custom Domain

1. In your domain registrar (GoDaddy, Namecheap, Cloudflare):
   - Add a `CNAME` record: `www` pointing to `your-service-name.onrender.com`.
   - Add an `ANAME` or `A` record pointing to the hosting provider's IP address.
2. In the hosting dashboard, add `halconcareer.com` and `www.halconcareer.com`.
3. Add the domains to `ALLOWED_HOSTS` in `.env`.
4. The provider automatically provisions a free Let's Encrypt SSL/TLS certificate.

---

## 11. Troubleshooting Common Issues

| Issue | Cause | Resolution |
| :--- | :--- | :--- |
| `ProgrammingError: relation does not exist` | Pending migrations | Run `python manage.py migrate` |
| Static files not styling in production | `collectstatic` was not run | Run `python manage.py collectstatic --no-input` and ensure `whitenoise.middleware.WhiteNoiseMiddleware` is enabled in `MIDDLEWARE`. |
| `DisallowedHost at /` | Host header not in `ALLOWED_HOSTS` | Add your domain or IP to `ALLOWED_HOSTS` in `.env`. |
| Resume upload returns `File size exceeds 5 MB` | File exceeds maximum limit | Instruct candidate to upload a resume under 5 MB. Adjust `DATA_UPLOAD_MAX_MEMORY_SIZE` if higher capacity is required. |
| Resume upload returns `Unsupported file format` | Candidate uploaded non-PDF/DOCX | Supported formats are strictly `.pdf`, `.docx`, and `.doc`. |

---

## 12. Corporate Ownership & Contact

**HALCON CAREER Recruitment & Staffing Consultancy**  
SCO 12–13, 2nd Floor, Phase 11, Mohali, Punjab – 160065  
Phone: +91 9216033444 / +91 8699000984  
Email: contact@halconcareer.com  
Hours: Monday - Friday: 9:30 AM – 6:30 PM | Saturday: 10:00 AM – 2:00 PM  
