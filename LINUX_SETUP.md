# Linux Development Setup - ReedManage

## Quick guide to develop ReedManage on Linux

---

## System Requirements

- **OS**: Ubuntu 20.04+ / Debian 11+ / Fedora 35+ / Any modern Linux distro
- **Python**: 3.9 or higher
- **Git**: For version control
- **Node.js**: For Tailwind CSS (optional if not modifying styles)

---

## Step 1: Install Dependencies

### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
```

### Fedora/RHEL:
```bash
sudo dnf install python3 python3-pip git
```

### Arch Linux:
```bash
sudo pacman -S python python-pip git
```

---

## Step 2: Transfer Project to Linux

### Option A: Clone from Git
```bash
# If you push your project to GitHub/GitLab
git clone https://github.com/yourusername/ReedDjango.git
cd ReedDjango/src
```

### Option B: Copy from macOS
```bash
# From macOS, copy to Linux via USB, network, or cloud
# Example using scp:
# scp -r /Users/takako/ReedDjango user@linux-machine:/home/user/

cd /path/to/ReedDjango/src
```

### Option C: Fresh Setup
```bash
# Download and extract your project files
cd ~/Projects
mkdir -p ReedDjango/src
cd ReedDjango/src
# Copy your files here
```

---

## Step 3: Set Up Virtual Environment

```bash
cd /path/to/ReedDjango/src

# Create virtual environment
python3 -m venv newenv

# Activate virtual environment
source newenv/bin/activate

# You should see (newenv) in your prompt
```

---

## Step 4: Install Python Packages

```bash
# Make sure virtual environment is activated
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

**Note**: If you get errors with some packages, you may need system dependencies:

```bash
# For Pillow (image processing)
sudo apt install -y python3-dev libjpeg-dev zlib1g-dev

# For PostgreSQL (if using)
sudo apt install -y libpq-dev

# Then retry
pip install -r requirements.txt
```

---

## Step 5: Set Up Environment Variables

```bash
# Copy the example .env file
cp .env.example .env

# Or create new one
nano .env
```

Add to `.env`:
```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
EMAIL_VERIFICATION_REQUIRED=False
```

---

## Step 6: Set Up Database

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Initialize parameters (optional)
python manage.py init_parameters

# Import reed data (optional)
python manage.py import_reeds
```

---

## Step 7: Run Development Server

```bash
# Activate virtual environment if not already active
source newenv/bin/activate

# Run server
python manage.py runserver

# Or bind to all interfaces for device testing
python manage.py runserver 0.0.0.0:8000
```

Access at:
- **Local**: http://localhost:8000
- **Network devices**: http://YOUR_LINUX_IP:8000

---

## Step 8: Install Tailwind CSS (Optional)

If you want to modify styles:

```bash
# Install Node.js
sudo apt install -y nodejs npm  # Ubuntu/Debian
# or
sudo dnf install nodejs npm     # Fedora

# Install Tailwind dependencies
cd theme/static_src
npm install

# Return to project root
cd ../..

# Start Tailwind in watch mode (separate terminal)
python manage.py tailwind start
```

---

## File Permissions (Important!)

On Linux, make sure the database and media files are writable:

```bash
# Give proper permissions
chmod 664 db.sqlite3
chmod -R 755 static/
chmod -R 755 media/ 2>/dev/null || true

# If running as different user
chown -R yourusername:yourusername .
```

---

## Testing on Network Devices

### 1. Find Your Linux Machine's IP:
```bash
# Get IP address
ip addr show | grep "inet " | grep -v 127.0.0.1
# or
hostname -I
```

### 2. Allow Firewall Access:
```bash
# Ubuntu/Debian with ufw
sudo ufw allow 8000/tcp

# Fedora with firewalld
sudo firewall-cmd --add-port=8000/tcp --permanent
sudo firewall-cmd --reload

# Or disable firewall temporarily for testing
sudo ufw disable  # Ubuntu
sudo systemctl stop firewalld  # Fedora
```

### 3. Update Django Settings:
Edit `src/reedmanage/settings.py`:
```python
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'YOUR_LINUX_IP', '*']
```

### 4. Start Server:
```bash
python manage.py runserver 0.0.0.0:8000
```

### 5. Access from Phone/Tablet:
```
http://YOUR_LINUX_IP:8000
```

---

## Differences from macOS

### Identical:
- All Python code works exactly the same
- Virtual environment activation: `source newenv/bin/activate`
- Django commands: All the same
- Database file: `db.sqlite3` is portable

### Potential Differences:
- **File paths**: Use `/home/user/` instead of `/Users/takako/`
- **Python command**: Usually `python3` instead of `python`
- **Permissions**: Linux is stricter about file permissions
- **Case sensitivity**: Linux filesystems are case-sensitive

---

## Development Workflow on Linux

```bash
# Start development session
cd /path/to/ReedDjango/src
source newenv/bin/activate
python manage.py runserver

# In another terminal (if modifying CSS)
cd /path/to/ReedDjango/src
source newenv/bin/activate
python manage.py tailwind start

# Run tests
python manage.py test

# Make migrations after model changes
python manage.py makemigrations
python manage.py migrate
```

---

## IDE Recommendations for Linux

1. **VS Code**: `sudo snap install code --classic`
2. **PyCharm Community**: Free, excellent Django support
3. **Vim/Neovim**: With Python plugins
4. **Emacs**: With Python mode

---

## Useful Linux Commands

```bash
# Check Python version
python3 --version

# Check which Python is being used
which python3

# Check installed packages
pip list

# Find processes using port 8000
sudo lsof -i :8000

# Kill Django server if stuck
pkill -f runserver

# Check disk space
df -h

# Check memory usage
free -h

# Monitor system resources
htop
```

---

## Troubleshooting

### Issue: "Permission denied" when running server
```bash
chmod +x manage.py
```

### Issue: Port 8000 already in use
```bash
# Find what's using the port
sudo lsof -i :8000

# Kill it
sudo kill -9 <PID>

# Or use different port
python manage.py runserver 8001
```

### Issue: Database locked
```bash
# Check if another process is using it
fuser db.sqlite3

# Kill the process
sudo fuser -k db.sqlite3
```

### Issue: Static files not found
```bash
python manage.py collectstatic --noinput
```

### Issue: Module not found
```bash
# Make sure virtual environment is activated
source newenv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

---

## Performance Tips

Linux typically runs Django faster than macOS due to:
- More efficient file system operations
- Better memory management
- Optimized system calls

Your app should run smoothly on even modest Linux hardware!

---

## Switching Between Linux and macOS

The entire project is portable! Just:

1. Commit changes to Git on one system
2. Pull changes on the other system
3. Reactivate virtual environment on that system
4. Continue development

The `db.sqlite3` file and all code work identically on both platforms.

---

**Ready to develop on Linux!** Your Django app will run exactly the same as on macOS.
