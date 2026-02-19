# Heroku Deployment Guide - ReedManage

## Complete guide to deploy ReedManage privately on Heroku for device testing

---

## Prerequisites

1. **Heroku Account**: Sign up at https://heroku.com (free tier available)
2. **Heroku CLI**: Install from https://devcenter.heroku.com/articles/heroku-cli
3. **Git**: Already set up in your project
4. **PostgreSQL**: Heroku uses PostgreSQL (not SQLite)

---

## Step 1: Install Heroku CLI and Login

```bash
# Install Heroku CLI (macOS)
brew tap heroku/brew && brew install heroku

# Or on Linux
curl https://cli-assets.heroku.com/install.sh | sh

# Login to Heroku
heroku login
```

---

## Step 2: Update Settings for Heroku

Add this to the **bottom** of `src/reedmanage/settings.py`:

```python
# Heroku Configuration
import dj_database_url

# Update ALLOWED_HOSTS for Heroku
if 'DYNO' in os.environ:  # Running on Heroku
    ALLOWED_HOSTS = ['.herokuapp.com', '127.0.0.1', 'localhost']

    # Database configuration for Heroku PostgreSQL
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    )

    # Static files configuration for Heroku
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

    # WhiteNoise for serving static files
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    # Security settings for production
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
```

---

## Step 3: Add dj-database-url to Requirements

```bash
cd src
echo "dj-database-url==2.1.0" >> requirements.txt
```

---

## Step 4: Create Heroku App (PRIVATE)

```bash
cd /Users/takako/ReedDjango/src

# Create a Heroku app
heroku create your-app-name-here

# Example: heroku create reedmanage-takako-test
# This creates: https://reedmanage-takako-test.herokuapp.com

# Make it PRIVATE (not searchable/indexable)
# This is done through environment variables below
```

---

## Step 5: Configure Environment Variables

```bash
# Set production environment variables
heroku config:set DJANGO_SECRET_KEY="your-super-secret-key-generate-new-one"
heroku config:set DJANGO_DEBUG=False
heroku config:set EMAIL_VERIFICATION_REQUIRED=False

# Optional: Add email settings later when ready
# heroku config:set EMAIL_HOST_USER="your-email@gmail.com"
# heroku config:set EMAIL_HOST_PASSWORD="your-app-password"
```

**Generate a secure secret key:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Step 6: Add PostgreSQL Database

```bash
# Add free PostgreSQL database
heroku addons:create heroku-postgresql:essential-0

# This automatically sets DATABASE_URL environment variable
```

---

## Step 7: Deploy to Heroku

```bash
# Make sure you're in the src directory
cd /Users/takako/ReedDjango/src

# Initialize git if not already done (should already exist)
# git init

# Add Heroku remote (if not added during heroku create)
# heroku git:remote -a your-app-name

# Commit any recent changes
git add .
git commit -m "Prepare for Heroku deployment"

# Push to Heroku (deploys from src/ directory)
git subtree push --prefix src heroku main

# Or if you're deploying the whole repo:
# git push heroku main
```

---

## Step 8: Run Database Migrations

```bash
# Run migrations on Heroku
heroku run python manage.py migrate

# Create superuser on Heroku
heroku run python manage.py createsuperuser

# Optional: Initialize parameters
heroku run python manage.py init_parameters
```

---

## Step 9: Keep It PRIVATE for Testing

### Option A: Use Authentication (Recommended)
Your app already requires login - only users with accounts can access!

### Option B: Add Basic HTTP Authentication (Extra Security)
Add this middleware to `settings.py`:

```python
# Add to MIDDLEWARE when on Heroku
if 'DYNO' in os.environ:
    MIDDLEWARE.insert(0, 'reedmanage.middleware.BasicAuthMiddleware')
```

Create `src/reedmanage/middleware.py`:
```python
from django.http import HttpResponse
import base64

class BasicAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) == 2 and auth[0].lower() == "basic":
                username, password = base64.b64decode(auth[1]).decode('utf-8').split(':')
                if username == 'test' and password == 'reedtest2026':  # Change these!
                    return self.get_response(request)

        response = HttpResponse('Unauthorized', status=401)
        response['WWW-Authenticate'] = 'Basic realm="ReedManage Testing"'
        return response
```

Set credentials:
```bash
heroku config:set BASIC_AUTH_USER=test
heroku config:set BASIC_AUTH_PASS=your-secure-password
```

### Option C: Block Search Engines
Already done! Your `base.html` should include:
```html
<meta name="robots" content="noindex, nofollow">
```

---

## Step 10: Test on Devices

```bash
# Open your app
heroku open

# Or visit directly
# https://your-app-name.herokuapp.com
```

### Testing Checklist:
- [ ] iPhone Safari - Visit URL, login, test features
- [ ] Android Chrome - Visit URL, login, test features
- [ ] Install as PWA on both devices (Add to Home Screen)
- [ ] Test offline functionality
- [ ] Test add reed, view reeds, statistics
- [ ] Test data export (CSV, Excel, JSON)
- [ ] Test help pages and tooltips

---

## Useful Heroku Commands

```bash
# View logs
heroku logs --tail

# Check app status
heroku ps

# Open database console
heroku pg:psql

# Run Django shell
heroku run python manage.py shell

# Restart app
heroku restart

# View environment variables
heroku config

# Scale dynos (free tier = 1)
heroku ps:scale web=1

# Delete app (when done testing)
heroku apps:destroy --app your-app-name
```

---

## Troubleshooting

### Issue: Static files not loading
```bash
# Collect static files
heroku run python manage.py collectstatic --noinput

# Check WhiteNoise is in MIDDLEWARE
heroku run python manage.py check --deploy
```

### Issue: Database errors
```bash
# Check database connection
heroku pg:info

# Run migrations again
heroku run python manage.py migrate
```

### Issue: 500 errors
```bash
# Check logs
heroku logs --tail

# View detailed error
heroku run python manage.py check
```

### Issue: App won't start
```bash
# Check Procfile exists in src/
cat Procfile

# Check gunicorn is installed
heroku run pip list | grep gunicorn
```

---

## Cost Information (Updated January 2025)

**Heroku eliminated free tiers in November 2022.** Here are current pricing options:

### Option 1: Eco Dynos (Budget Option)
- **Eco Dyno**: $5/month
  - 1000 dyno hours/month
  - Sleeps after 30 minutes of inactivity
  - Wakes automatically on first request (slight delay)
- **Mini PostgreSQL**: $5/month
  - 10GB storage, 20 connections
- **Total: $10/month**
- **Best for**: Testing when you don't mind sleep delays

### Option 2: Basic Dynos (Always-On)
- **Basic Dyno**: $7/month
  - Never sleeps
  - Better for consistent device testing
- **Mini PostgreSQL**: $5/month
- **Total: $12/month**
- **Best for**: Professional testing/demos

### Free Alternative: Use ngrok Instead
For free device testing, see **NGROK_SETUP.md** (no Heroku needed!)
- Run app locally on your Mac
- Expose via public URL with ngrok
- Test on any device for free
- Perfect for short testing sessions

### To Avoid/Minimize Costs:
- **Use ngrok for free testing** (see NGROK_SETUP.md)
- Delete Heroku app after testing: `heroku apps:destroy --app your-app-name`
- Scale down when not testing: `heroku ps:scale web=0`
- Only deploy to Heroku when you need 24/7 availability

---

## Security Best Practices

1. **Never commit sensitive data**: Use environment variables
2. **Change SECRET_KEY**: Generate a new one for production
3. **Enable HTTPS**: Already configured in settings
4. **Limit access**: Use Basic Auth or keep login-required
5. **Monitor logs**: Check `heroku logs` regularly
6. **Rate limiting**: Already configured (django-ratelimit, django-axes)

---

## Migrating Data from SQLite to PostgreSQL

If you want to migrate your existing data:

```bash
# On your local machine:
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > data.json

# Deploy to Heroku
git add data.json
git commit -m "Add data dump"
git subtree push --prefix src heroku main

# On Heroku:
heroku run python manage.py loaddata data.json
```

---

## When You're Done Testing

```bash
# Stop app
heroku ps:scale web=0

# Or delete entirely
heroku apps:destroy --app your-app-name --confirm your-app-name
```

---

## Need Help?

- Heroku Docs: https://devcenter.heroku.com/articles/django-app-configuration
- Django Deployment: https://docs.djangoproject.com/en/4.2/howto/deployment/
- Check logs: `heroku logs --tail`
- Contact: Use the contact form in the app

---

**Ready to deploy!** Follow the steps above and your app will be live for private device testing in about 10 minutes.
