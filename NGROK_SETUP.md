# ngrok Setup Guide - Free Device Testing for ReedManage

## Quick guide to test your Django app on real devices (iPhone/Android) for FREE

---

## What is ngrok?

ngrok creates a secure public URL that tunnels to your local Django server. This lets you test your app on any device (phone, tablet) without deploying to Heroku.

**Perfect for:**
- Testing PWA features on real devices
- Quick device testing without paying for hosting
- Showing your app to others temporarily

**Free Tier:**
- 1 online ngrok process
- 40 connections/minute
- Random URL each time (upgradeable to custom domain)

---

## Step 1: ngrok is Already Installed!

✓ ngrok has been installed via Homebrew

Verify installation:
```bash
ngrok version
```

---

## Step 2: Create Free ngrok Account (Optional but Recommended)

Without an account, ngrok works but sessions are limited. With a free account, you get:
- Longer session times
- More connections
- Basic monitoring

```bash
# Sign up at ngrok.com (takes 30 seconds)
# Then authenticate (paste your authtoken from dashboard)
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```

**Get your authtoken:**
1. Visit https://dashboard.ngrok.com/signup
2. Sign up (free)
3. Copy your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
4. Run: `ngrok config add-authtoken YOUR_TOKEN`

---

## Step 3: Update Django Settings for ngrok

Add this to `src/reedmanage/settings.py` (if not already there):

```python
# At the top with other imports
import os

# Find ALLOWED_HOSTS and update it:
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '.ngrok-free.app',  # For ngrok tunnels
    '.ngrok.io',        # For older ngrok versions
]

# Optional: Add CSRF trusted origins for ngrok
CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.app',
    'https://*.ngrok.io',
]
```

---

## Step 4: Start Your Django App

```bash
cd /Users/takako/ReedDjango/src
source venv/bin/activate  # Or your virtual environment
python manage.py runserver 8000
```

Keep this terminal running!

---

## Step 5: Start ngrok (New Terminal)

Open a **new terminal window** and run:

```bash
ngrok http 8000
```

You'll see something like:
```
ngrok

Session Status                online
Account                       Your Name (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**Your public URL is:** `https://abc123.ngrok-free.app`

---

## Step 6: Test on Your Devices

### On iPhone:
1. Open Safari
2. Go to: `https://abc123.ngrok-free.app` (your ngrok URL)
3. Click "Visit Site" (ngrok warning page)
4. You'll see ReedManage login page!
5. Login and test features

### On Android:
1. Open Chrome
2. Go to: `https://abc123.ngrok-free.app` (your ngrok URL)
3. Click "Visit Site" (ngrok warning page)
4. Login and test

### Install PWA:
- **iPhone**: Safari menu → "Add to Home Screen"
- **Android**: Chrome menu → "Add to Home Screen" or "Install App"

---

## Step 7: Monitor Traffic (Optional)

Open http://127.0.0.1:4040 in your browser to see:
- All HTTP requests
- Response times
- Request/response details
- Great for debugging!

---

## Testing Checklist

Use your ngrok URL to test:
- [ ] Login page loads on iPhone/Android
- [ ] Can login successfully
- [ ] Dashboard shows statistics
- [ ] Can add a new reed
- [ ] Can view reeds list
- [ ] Can edit reed data
- [ ] Can export data (CSV, Excel, JSON)
- [ ] Help tooltips work
- [ ] Contact form submits
- [ ] Legal pages load (Privacy, Terms)
- [ ] PWA installs correctly
- [ ] Offline mode works (after install)

---

## Quick Reference Commands

```bash
# Start Django (Terminal 1)
cd /Users/takako/ReedDjango/src
source venv/bin/activate
python manage.py runserver 8000

# Start ngrok (Terminal 2)
ngrok http 8000

# Stop ngrok
# Press Ctrl+C in ngrok terminal

# Stop Django
# Press Ctrl+C in Django terminal
```

---

## ngrok vs Heroku: When to Use Each

### Use ngrok when:
- ✓ Quick device testing (free)
- ✓ Showing app to 1-2 people temporarily
- ✓ You're actively developing/testing
- ✓ You don't need 24/7 availability
- ✓ You want to save money

### Use Heroku when:
- ✓ Need 24/7 availability
- ✓ Multiple users accessing simultaneously
- ✓ Professional demos/portfolio
- ✓ Don't want to keep your Mac running
- ✓ Need production-grade database

---

## Troubleshooting

### Issue: "Invalid Host header" error
**Solution:** Make sure `.ngrok-free.app` is in ALLOWED_HOSTS (see Step 3)

### Issue: ngrok URL changes every time
**Solution:** Free tier gives random URLs. To get a static domain:
- Upgrade to ngrok paid plan ($8/month)
- Or just use Heroku for permanent hosting

### Issue: "Visit Site" warning page
**Solution:** This is normal with free ngrok. Just click "Visit Site" button.

### Issue: Can't connect from phone
**Solution:**
- Make sure phone is on Wi-Fi (not just cellular)
- Make sure ngrok is running (check terminal)
- Try the HTTPS URL (not HTTP)

### Issue: CSRF verification failed
**Solution:** Add `CSRF_TRUSTED_ORIGINS` to settings.py (see Step 3)

---

## Security Notes

### Is ngrok secure?
- ✓ Uses HTTPS (encrypted traffic)
- ✓ Tunnels are temporary
- ✓ You control when it's running
- ✓ Login required for your app

### Best Practices:
1. **Only run ngrok when testing** (don't leave running)
2. **Share URL carefully** (anyone with URL can access)
3. **Use authentication** (your Django login protects data)
4. **Don't use for production** (use proper hosting instead)
5. **Monitor traffic** (use http://127.0.0.1:4040)

---

## Advanced: Custom ngrok Config

Create `~/.ngrok2/ngrok.yml` for custom settings:

```yaml
version: "2"
authtoken: YOUR_AUTHTOKEN
tunnels:
  reedmanage:
    proto: http
    addr: 8000
    inspect: true
```

Then start with:
```bash
ngrok start reedmanage
```

---

## Cost Comparison

| Method | Cost | Pros | Cons |
|--------|------|------|------|
| **ngrok (Free)** | $0 | Instant, no deployment | Mac must stay on, random URL |
| **ngrok (Paid)** | $8/month | Custom domain | Mac must stay on |
| **Heroku Eco** | $10/month | 24/7, professional | Sleeps after 30min |
| **Heroku Basic** | $12/month | 24/7, no sleep | Costs more |

---

## When You're Done Testing

```bash
# Stop ngrok (Terminal 2)
Press Ctrl+C

# Stop Django (Terminal 1)
Press Ctrl+C
```

**That's it!** Your app is no longer accessible from the internet.

---

## Next Steps

1. **Test thoroughly** using the checklist above
2. **Fix any bugs** you find during device testing
3. **Decide on hosting:**
   - Keep using ngrok for free testing
   - Deploy to Heroku for 24/7 access ($10-12/month)
4. **Check MOBILE_TESTING_CHECKLIST.md** for complete PWA testing guide

---

## Need Help?

- ngrok Docs: https://ngrok.com/docs
- ngrok Dashboard: https://dashboard.ngrok.com
- Check logs: Terminal where ngrok is running
- Monitor: http://127.0.0.1:4040

---

**Ready to test!** Your app can be on your phone in less than 2 minutes using ngrok.
