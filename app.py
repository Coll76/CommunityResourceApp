from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
import json
from flask_migrate import Migrate

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///community_exchange.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    bio = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(120), nullable=True)
    reputation = db.Column(db.Integer, default=100)
    
    # Relationships
    resources = db.relationship('Resource', backref='owner', lazy=True)
    requests = db.relationship('Request', backref='requester', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    condition = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    is_available = db.Column(db.Boolean, default=True)
    pickup_location = db.Column(db.String(120), nullable=True)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    requests = db.relationship('Request', backref='resource', lazy=True)

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=True)
    date_requested = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected, completed
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'), nullable=False)

class Exchange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_completed = db.Column(db.DateTime, default=datetime.utcnow)
    donor_feedback = db.Column(db.Text, nullable=True)
    receiver_feedback = db.Column(db.Text, nullable=True)
    donor_rating = db.Column(db.Integer, nullable=True)
    receiver_rating = db.Column(db.Integer, nullable=True)
    
    # Foreign keys
    request_id = db.Column(db.Integer, db.ForeignKey('request.id'), nullable=False)
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    """Home page with recent listings and impact statistics"""
    recent_resources = Resource.query.filter_by(is_available=True).order_by(Resource.date_posted.desc()).limit(5).all()
    
    # Get impact statistics
    total_resources = Resource.query.count()
    completed_exchanges = Exchange.query.count()
    active_users = User.query.count()
    
    return render_template('index.html', 
                          recent_resources=recent_resources,
                          total_resources=total_resources, 
                          completed_exchanges=completed_exchanges,
                          active_users=active_users)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        location = request.form.get('location')
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html')
        
        # Create new user
        new_user = User(username=username, email=email, location=location)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Invalid email or password', 'danger')
            return render_template('login.html')
        
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        return redirect(next_page or url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Log out the current user"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    """User profile page showing resources and requests"""
    user_resources = Resource.query.filter_by(user_id=current_user.id).order_by(Resource.date_posted.desc()).all()
    user_requests = Request.query.filter_by(user_id=current_user.id).order_by(Request.date_requested.desc()).all()
    
    # Get completed exchanges
    completed_donations = Exchange.query.filter_by(donor_id=current_user.id).all()
    completed_received = Exchange.query.filter_by(receiver_id=current_user.id).all()
    
    return render_template('profile.html',
                          user=current_user,
                          resources=user_resources,
                          requests=user_requests,
                          donations=completed_donations,
                          received=completed_received)

@app.route('/resources')
def resources():
    """Browse all available resources"""
    category = request.args.get('category', '')
    location = request.args.get('location', '')
    query = request.args.get('query', '')
    
    resources_query = Resource.query.filter_by(is_available=True)
    
    if category:
        resources_query = resources_query.filter_by(category=category)
    
    if location:
        # Join with user table to filter by user location
        resources_query = resources_query.join(User).filter(User.location.like(f'%{location}%'))
    
    if query:
        resources_query = resources_query.filter(
            db.or_(
                Resource.title.like(f'%{query}%'),
                Resource.description.like(f'%{query}%')
            )
        )
    
    resources = resources_query.order_by(Resource.date_posted.desc()).all()
    
    # Get all distinct categories for filtering
    categories = db.session.query(Resource.category).distinct().all()
    categories = [c[0] for c in categories]
    
    return render_template('resources.html',
                          resources=resources,
                          categories=categories,
                          selected_category=category,
                          location=location,
                          query=query)

@app.route('/resource/<int:resource_id>')
def resource_detail(resource_id):
    """View details of a specific resource"""
    resource = Resource.query.get_or_404(resource_id)
    
    # Check if current user has already requested this resource
    user_request = None
    if current_user.is_authenticated:
        user_request = Request.query.filter_by(
            user_id=current_user.id,
            resource_id=resource_id
        ).first()
    
    return render_template('resource_detail.html',
                          resource=resource,
                          user_request=user_request)

@app.route('/resource/new', methods=['GET', 'POST'])
@login_required
def new_resource():
    """Create a new resource listing"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        condition = request.form.get('condition')
        quantity = int(request.form.get('quantity', 1))
        pickup_location = request.form.get('pickup_location')
        
        new_resource = Resource(
            title=title,
            description=description,
            category=category,
            condition=condition,
            quantity=quantity,
            pickup_location=pickup_location,
            user_id=current_user.id
        )
        
        db.session.add(new_resource)
        db.session.commit()
        
        flash('Resource added successfully!', 'success')
        return redirect(url_for('resource_detail', resource_id=new_resource.id))
    
    return render_template('resource_form.html')

@app.route('/resource/<int:resource_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_resource(resource_id):
    """Edit an existing resource"""
    resource = Resource.query.get_or_404(resource_id)
    
    # Check if current user is the owner
    if resource.user_id != current_user.id:
        flash('You do not have permission to edit this resource', 'danger')
        return redirect(url_for('resource_detail', resource_id=resource_id))
    
    if request.method == 'POST':
        resource.title = request.form.get('title')
        resource.description = request.form.get('description')
        resource.category = request.form.get('category')
        resource.condition = request.form.get('condition')
        resource.quantity = int(request.form.get('quantity', 1))
        resource.pickup_location = request.form.get('pickup_location')
        resource.is_available = 'is_available' in request.form
        
        db.session.commit()
        
        flash('Resource updated successfully!', 'success')
        return redirect(url_for('resource_detail', resource_id=resource_id))
    
    return render_template('resource_form.html', resource=resource)

@app.route('/resource/<int:resource_id>/request', methods=['POST'])
@login_required
def request_resource(resource_id):
    """Request a specific resource"""
    resource = Resource.query.get_or_404(resource_id)
    
    # Check if resource is still available
    if not resource.is_available:
        flash('This resource is no longer available', 'danger')
        return redirect(url_for('resource_detail', resource_id=resource_id))
    
    # Check if user is not requesting their own resource
    if resource.user_id == current_user.id:
        flash('You cannot request your own resource', 'danger')
        return redirect(url_for('resource_detail', resource_id=resource_id))
    
    # Check if user has already requested this resource
    existing_request = Request.query.filter_by(
        user_id=current_user.id,
        resource_id=resource_id
    ).first()
    
    if existing_request:
        flash('You have already requested this resource', 'info')
        return redirect(url_for('resource_detail', resource_id=resource_id))
    
    message = request.form.get('message', '')
    
    new_request = Request(
        message=message,
        user_id=current_user.id,
        resource_id=resource_id
    )
    
    db.session.add(new_request)
    db.session.commit()
    
    flash('Request submitted successfully!', 'success')
    return redirect(url_for('resource_detail', resource_id=resource_id))

@app.route('/requests')
@login_required
def manage_requests():
    """Manage incoming requests for user's resources"""
    # Get resources owned by current user
    user_resources = Resource.query.filter_by(user_id=current_user.id).all()
    resource_ids = [r.id for r in user_resources]
    
    # Get requests for these resources
    incoming_requests = Request.query.filter(
        Request.resource_id.in_(resource_ids)
    ).order_by(Request.date_requested.desc()).all()
    
    return render_template('manage_requests.html', 
                          requests=incoming_requests)

@app.route('/request/<int:request_id>/<action>', methods=['POST'])
@login_required
def handle_request(request_id, action):
    """Accept or reject a resource request"""
    req = Request.query.get_or_404(request_id)
    resource = Resource.query.get(req.resource_id)
    
    # Check if current user owns the resource
    if resource.user_id != current_user.id:
        flash('You do not have permission to manage this request', 'danger')
        return redirect(url_for('manage_requests'))
    
    if action == 'accept':
        req.status = 'accepted'
        flash('Request accepted!', 'success')
    elif action == 'reject':
        req.status = 'rejected'
        flash('Request rejected', 'info')
    elif action == 'complete':
        if req.status != 'accepted':
            flash('Only accepted requests can be completed', 'danger')
            return redirect(url_for('manage_requests'))
        
        req.status = 'completed'
        resource.is_available = False
        
        # Create a new exchange record
        exchange = Exchange(
            request_id=req.id,
            donor_id=current_user.id,
            receiver_id=req.user_id
        )
        
        db.session.add(exchange)
        flash('Exchange completed!', 'success')
    
    db.session.commit()
    return redirect(url_for('manage_requests'))

@app.route('/exchange/<int:exchange_id>/feedback', methods=['GET', 'POST'])
@login_required
def exchange_feedback(exchange_id):
    """Provide feedback for a completed exchange"""
    exchange = Exchange.query.get_or_404(exchange_id)
    
    # Check if current user is part of this exchange
    if current_user.id != exchange.donor_id and current_user.id != exchange.receiver_id:
        flash('You do not have permission to provide feedback for this exchange', 'danger')
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        rating = int(request.form.get('rating', 5))
        feedback = request.form.get('feedback', '')
        
        if current_user.id == exchange.donor_id:
            exchange.donor_rating = rating
            exchange.donor_feedback = feedback
            
            # Update receiver reputation
            receiver = User.query.get(exchange.receiver_id)
            receiver.reputation += rating - 3  # Adjust reputation based on rating
        else:
            exchange.receiver_rating = rating
            exchange.receiver_feedback = feedback
            
            # Update donor reputation
            donor = User.query.get(exchange.donor_id)
            donor.reputation += rating - 3  # Adjust reputation based on rating
        
        db.session.commit()
        
        flash('Feedback submitted successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('feedback_form.html', exchange=exchange)

@app.route('/impact')
def impact():
    """Community impact visualization page"""
    # Get total stats
    total_resources = Resource.query.count()
    completed_exchanges = Exchange.query.count()
    active_users = User.query.count()
    
    # Get category distribution
    categories = db.session.query(
        Resource.category, 
        db.func.count(Resource.id)
    ).group_by(Resource.category).all()
    
    # Get monthly exchange data for charts
    six_months_ago = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    for _ in range(5):
        if six_months_ago.month == 1:
            six_months_ago = six_months_ago.replace(year=six_months_ago.year-1, month=12)
        else:
            six_months_ago = six_months_ago.replace(month=six_months_ago.month-1)
    
    monthly_exchanges = db.session.query(
        db.func.strftime('%Y-%m', Exchange.date_completed).label('month'),
        db.func.count(Exchange.id)
    ).filter(Exchange.date_completed >= six_months_ago).group_by('month').all()
    
    return render_template('impact.html',
                          total_resources=total_resources,
                          completed_exchanges=completed_exchanges,
                          active_users=active_users,
                          categories=categories,
                          monthly_exchanges=monthly_exchanges)

@app.route('/api/resources')
def api_resources():
    """API endpoint for resources data"""
    resources = Resource.query.filter_by(is_available=True).order_by(Resource.date_posted.desc()).all()
    
    results = []
    for resource in resources:
        results.append({
            'id': resource.id,
            'title': resource.title,
            'category': resource.category,
            'condition': resource.condition,
            'date_posted': resource.date_posted.strftime('%Y-%m-%d'),
            'owner': resource.owner.username,
            'location': resource.owner.location
        })
    
    return jsonify(results)

@app.context_processor
def utility_processor():
    """Add utility functions to template context"""
    def time_since(date):
        """Return human readable time since given date"""
        now = datetime.utcnow()
        delta = now - date
        
        if delta.days > 365:
            years = delta.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        if delta.days > 30:
            months = delta.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        if delta.days > 0:
            return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
        if delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        if delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        return "just now"
    
    return dict(time_since=time_since)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)