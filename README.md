# The Reed App

A data-driven web application for double reed players to systematically track, analyze, and optimize their reed-making process.

## Table of Contents
- [What is This?](#what-is-this)
- [The Problem](#the-problem)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Screenshots](#screenshots)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## What is This?

### For Non-Musicians
Double reed instruments (oboe, bassoon, English horn) use reeds made from natural cane that musicians handcraft themselves. Unlike store-bought guitar strings or drum sticks, professional oboists and bassoonists spend hours each week making reeds from scratch. The quality and characteristics of the cane significantly impact the instrument's sound, intonation, and playability.

**The Reed App** is a specialized data management system that helps musicians track variables like cane density, humidity, gouging machine settings, and performance ratings to identify patterns and improve their reed-making outcomes.

### For Musicians
If you've ever wondered why some pieces of cane make great reeds while others don't, this app helps you find answers. Track everything from cane brand and harvest year to density calculations and playing characteristics, then analyze your data to make better-informed decisions.

## The Problem

Reed making is both an art and a science, but most musicians rely on intuition and inconsistent note-taking. Key challenges include:

- **Inconsistent Results**: Similar-looking cane can produce vastly different results
- **Lost Knowledge**: Handwritten notes get lost, making it hard to learn from past successes
- **Multiple Variables**: Tracking 10+ parameters per reed (humidity, density, thickness, etc.) is overwhelming
- **No Analysis**: Without data visualization, it's hard to spot patterns and correlations
- **Time-Consuming**: Professional musicians make 50-200+ reeds per year with no systematic tracking

This app transforms reed making from guesswork into a data-driven process.

## Key Features

### Core Functionality
- **Dynamic Data Entry**: Customizable forms that show only the parameters you care about
- **Automated Calculations**: Built-in density calculator using dry/wet mass measurements
- **Reed Database**: Store unlimited reed records with unique IDs for easy tracking
- **User Settings**: Select which parameters to track (temperature, humidity, cane brand, etc.)
- **Weather Integration**: Automatic weather data capture for each reed entry

### Data Management
- **CRUD Operations**: Create, read, update, and delete reed records
- **Batch Entry**: Add multiple reeds efficiently
- **Search & Filter**: Find specific reeds by ID, date, or characteristics
- **Edit History**: Track changes over time as reeds age and break in

### Performance Tracking
Track subjective qualities on a 0-10 scale:
- Stiffness
- Playing ease
- Intonation
- Tone color
- Response
- Overall quality

### Physical Properties
Record measurable cane characteristics:
- Diameter
- Thickness
- Hardness
- Flexibility
- Density (manual or auto-calculated)
- Temperature & humidity at time of making

### Equipment & Materials
Document your setup:
- Cane brand
- Harvest year
- Gouging machine model
- Profile/shaper model
- Staple model
- Instrument (oboe, bassoon, etc.)

### User Management
- **Authentication**: Secure user accounts with password protection
- **Personal Data**: Each user sees only their own reed data
- **Account Management**: Update profile, change password, view statistics
- **Contact Form**: Built-in communication system

## Tech Stack

**Backend:**
- Python 3.9+
- Django 5.2.4
- SQLite (development) / PostgreSQL-ready (production)

**Frontend:**
- TailwindCSS 4.0
- Django Templates
- Vanilla JavaScript

**Key Libraries:**
- `django-widget-tweaks` - Enhanced form rendering
- `pandas` - Data analysis capabilities
- `requests` - Weather API integration
- `python-dotenv` - Environment variable management
- `django-browser-reload` - Hot reload in development

**Security:**
- CSRF protection
- SQL injection prevention
- Password hashing (Django default)
- Environment-based configuration
- Input validation and sanitization

## Screenshots

*Coming soon - showing data entry form, reed list view, and statistics dashboard*

## Getting Started

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Takakochan/ReedApp.git
cd ReedApp
```

2. **Create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
cd src
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your configuration:
```
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
OPENWEATHER_API_KEY=your-api-key-here  # Optional
EMAIL_HOST_USER=your-email@gmail.com   # Optional
EMAIL_HOST_PASSWORD=your-app-password  # Optional
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create a superuser**
```bash
python manage.py createsuperuser
```

7. **Run the development server**
```bash
python manage.py runserver
```

8. **Access the application**
Open your browser to `http://127.0.0.1:8000/`

## Usage

### First-Time Setup
1. Create an account or log in
2. Visit the **Settings** page
3. Select which parameters you want to track
4. Save your preferences

### Adding Reed Data
1. Click **Add Reed** from the navigation
2. Fill in your selected parameters
3. Assign a unique **Reed ID** (e.g., "OB-2024-001")
4. For density calculation, enter both m1 (dry mass) and m2 (wet mass)
5. Save the entry

### Managing Your Data
- **View All Reeds**: See your complete reed database
- **Edit Reed**: Click on any reed to update information
- **Delete Reed**: Remove entries you no longer need
- **Search**: Filter by reed ID, date, or other criteria

### Best Practices
- Use consistent Reed ID naming conventions
- Update performance ratings as reeds break in
- Take measurements in similar environmental conditions
- Record data immediately after making reeds for accuracy

## Development

### Project Structure
```
ReedApp/
├── src/
│   ├── reedmanage/          # Main project settings
│   ├── reedsdata/           # Core reed tracking app
│   ├── usersettings/        # User preferences app
│   ├── account/             # User management
│   ├── contact/             # Contact form
│   ├── templates/           # Shared templates
│   ├── static_project/      # Custom static files
│   └── manage.py
├── static_cdn/              # Collected static files
├── venv/                    # Virtual environment (not in git)
├── .env                     # Environment variables (not in git)
├── .gitignore
└── README.md
```

### Running Tests
```bash
python manage.py test
```

### Collecting Static Files
```bash
python manage.py collectstatic
```

### Database Migrations
After model changes:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Code Style
This project follows Django and Python best practices:
- PEP 8 style guide
- Django naming conventions
- Comprehensive comments for complex logic

## Contributing

Contributions are welcome! This project is particularly suited for:
- Musicians who understand reed making
- Developers interested in music technology
- Data scientists interested in acoustics

### How to Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Ideas for Contribution
- Data visualization and charts
- Statistical analysis of reed characteristics
- Mobile-responsive design improvements
- Export to CSV/Excel functionality
- Reed lifecycle tracking
- Comparison tools
- Multi-language support
- API for data access

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

Built with passion by a musician for musicians. Special thanks to the reed-making community for their insights and feedback.

## Contact

For questions, suggestions, or collaboration:
- GitHub: [@Takakochan](https://github.com/Takakochan)
- Project Link: [https://github.com/Takakochan/ReedApp](https://github.com/Takakochan/ReedApp)

---

**Note for Hiring Managers**: This project demonstrates full-stack web development skills including:
- RESTful architecture and MVC pattern
- Database design and ORM usage
- User authentication and authorization
- Form validation and data sanitization
- Responsive UI design
- Security best practices
- Environment-based configuration
- Version control with Git
- Documentation and code organization

The domain (reed making) is specialized, but the technical implementation showcases transferable skills applicable to any data management system: inventory tracking, laboratory data, quality control, recipe management, etc.
