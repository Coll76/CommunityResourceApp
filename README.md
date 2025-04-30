# Community Exchange Platform

A Flask-based web application that facilitates resource sharing within communities, allowing users to offer unused items and request resources from others.

![Community Exchange Platform](https://via.placeholder.com/800x400?text=Community+Exchange+Platform)

## 🌟 Features

- **User Authentication**: Secure registration and login system
- **Resource Management**: Post, edit, and manage resource listings
- **Request System**: Request items and manage incoming requests
- **Exchange Tracking**: Complete exchanges and provide feedback
- **Reputation System**: Build trust through user ratings
- **Impact Visualization**: Track community impact through statistics and charts
- **Search & Filter**: Find resources by category, location, or keywords
- **Responsive Design**: Works on desktop and mobile devices

## 📋 Prerequisites

- Python 3.8+
- pip
- SQLite (default) or PostgreSQL
- Virtual environment (recommended)

## 🚀 Installation

1. **Clone the repository**

```bash
git clone https://github.com/Coll76/CommunityResourceApp.git
cd CommunityResourceApp
```

2. **Create and activate a virtual environment**

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Create a .env file**

Create a `.env` file in the project root with the following variables:

```
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///community_exchange.db
# For PostgreSQL use: postgresql://username:password@localhost/community_exchange
```

5. **Initialize the database**

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 🏃‍♂️ Running the Application

```bash
# Development mode
flask run --debug

# Production mode
flask run
```

Visit `http://127.0.0.1:5000` in your browser to access the application.

## 🔄 Application Workflow

1. **Users register and create profiles**
2. **Resource owners post available items**
3. **Users browse and request resources**
4. **Owners accept/reject requests**
5. **Exchanges are completed with handover**
6. **Users provide feedback and ratings**

## 🏗️ Project Structure

```
community_exchange/
├── app.py                  # Main application file
├── templates/              # HTML templates
│   ├── index.html          # Home page
│   ├── register.html       # Registration page
│   ├── login.html          # Login page
│   ├── profile.html        # User profile page
│   ├── resources.html      # Resource browsing page
│   ├── resource_detail.html # Individual resource page
│   ├── resource_form.html  # Form for adding/editing resources
│   ├── manage_requests.html # Request management page
│   ├── feedback_form.html  # Exchange feedback form
│   └── impact.html         # Community impact visualization
├── static/                 # Static files (CSS, JS, images)
├── migrations/             # Database migrations
├── .env                    # Environment variables
└── requirements.txt        # Python dependencies
```

## 📝 API Endpoints

- `/api/resources` - JSON API for available resources

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🔒 Security Considerations

- User passwords are securely hashed using Werkzeug's security functions
- Form validation to prevent common web vulnerabilities
- CSRF protection for all forms
- SQLAlchemy ORM used to prevent SQL injection

## 📚 Dependencies

- Flask: Web framework
- Flask-SQLAlchemy: ORM for database operations
- Flask-Login: User authentication
- Flask-Migrate: Database migrations
- Werkzeug: Security utilities
- python-dotenv: Environment variable management

## 🚀 Deployment

### Heroku Deployment

```bash
# Install Heroku CLI and login
heroku create community-resource-app
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
heroku run flask db upgrade
```

### Docker Deployment

```bash
# Build and run with Docker
docker build -t community-resource-app .
docker run -p 5000:5000 community-resource-app
```

## 📊 Database Schema

- **User**: User accounts and profiles
- **Resource**: Items available for exchange
- **Request**: Resource requests from users
- **Exchange**: Completed transactions with feedback

## 🧪 Running Tests

```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest tests/
```

## 🔮 Future Enhancements

- Direct messaging between users
- Image uploads for resources
- Geolocation for proximity-based matching
- Calendar integration for pickup scheduling
- Mobile app version

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Coll76 - [GitHub Profile](https://github.com/Coll76)

## 🙏 Acknowledgments

- Flask documentation and community
- Contributors and testers
- Everyone who helped shape the project
