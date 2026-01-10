from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = ''
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vendorshub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Indian States
INDIAN_STATES = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
    'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
    'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
    'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
    'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
    'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Puducherry'
]

BUSINESS_CATEGORIES = [
    'Restaurant', 'Cafe', 'Grocery Store', 'Salon', 'Pharmacy', 
    'Electronics Shop', 'Clothing Store', 'Hardware Store', 'Bakery',
    'Medical Clinic', 'Gym', 'Book Store', 'Other'
]

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'vendor' or 'customer'
    created_at = db.Column(db.DateTime, default=datetime.today)
    
    vendor = db.relationship('Vendor', backref='user', uselist=False)
    reviews = db.relationship('Review', backref='customer', lazy=True)

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    business_name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    state = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    image_path = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.today)
    
    reviews = db.relationship('Review', backref='vendor', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hygiene_rating = db.Column(db.Integer, nullable=False)
    necessities_available = db.Column(db.Boolean, nullable=False)
    staff_rating = db.Column(db.Integer, nullable=False)
    pricing_rating = db.Column(db.Integer, nullable=False)
    overall_rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text)
    image_path = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.today)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route('/')
def index():
    search_query = request.args.get('search', '')
    category = request.args.get('category', '')
    city = request.args.get('city', '')
    
    vendors = Vendor.query
    
    if search_query:
        vendors = vendors.filter(
            (Vendor.business_name.contains(search_query)) |
            (Vendor.city.contains(search_query)) |
            (Vendor.category.contains(search_query))
        )
    
    if category:
        vendors = vendors.filter_by(category=category)
    
    if city:
        vendors = vendors.filter(Vendor.city.contains(city))
    
    vendors = vendors.all()
    
    # Calculate average ratings
    vendor_data = []
    for vendor in vendors:
        avg_rating = db.session.query(db.func.avg(Review.overall_rating)).filter_by(vendor_id=vendor.id).scalar()
        review_count = Review.query.filter_by(vendor_id=vendor.id).count()
        vendor_data.append({
            'vendor': vendor,
            'avg_rating': round(avg_rating, 1) if avg_rating else 0,
            'review_count': review_count
        })
    
    # Sort by rating
    vendor_data.sort(key=lambda x: x['avg_rating'], reverse=True)
    
    top_vendors = vendor_data[:6]
    recent_vendors = sorted(vendors, key=lambda x: x.created_at, reverse=True)[:6]
    
    return render_template('index.html', 
                         top_vendors=top_vendors,
                         recent_vendors=recent_vendors,
                         categories=BUSINESS_CATEGORIES,
                         search_query=search_query)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            if user.role == 'vendor':
                return redirect(next_page) if next_page else redirect(url_for('vendor_dashboard'))
            else:
                return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/vendor/dashboard')
@login_required
def vendor_dashboard():
    if current_user.role != 'vendor':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    vendor = Vendor.query.filter_by(user_id=current_user.id).first()
    
    if vendor:
        reviews = Review.query.filter_by(vendor_id=vendor.id).all()
        avg_rating = db.session.query(db.func.avg(Review.overall_rating)).filter_by(vendor_id=vendor.id).scalar()
        avg_hygiene = db.session.query(db.func.avg(Review.hygiene_rating)).filter_by(vendor_id=vendor.id).scalar()
        avg_staff = db.session.query(db.func.avg(Review.staff_rating)).filter_by(vendor_id=vendor.id).scalar()
        avg_pricing = db.session.query(db.func.avg(Review.pricing_rating)).filter_by(vendor_id=vendor.id).scalar()
        
        stats = {
            'total_reviews': len(reviews),
            'avg_rating': round(avg_rating, 1) if avg_rating else 0,
            'avg_hygiene': round(avg_hygiene, 1) if avg_hygiene else 0,
            'avg_staff': round(avg_staff, 1) if avg_staff else 0,
            'avg_pricing': round(avg_pricing, 1) if avg_pricing else 0
        }
        
        return render_template('vendor_dashboard.html', vendor=vendor, reviews=reviews, stats=stats)
    
    return render_template('vendor_dashboard.html', vendor=None)

@app.route('/vendor/create', methods=['GET', 'POST'])
@login_required
def create_vendor():
    if current_user.role != 'vendor':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if Vendor.query.filter_by(user_id=current_user.id).first():
        flash('You already have a business listing', 'error')
        return redirect(url_for('vendor_dashboard'))
    
    if request.method == 'POST':
        state = request.form.get('state')
        
        if state not in INDIAN_STATES:
            flash('Please select a valid Indian state', 'error')
            return redirect(url_for('create_vendor'))
        
        business_name = request.form.get('business_name')
        category = request.form.get('category')
        description = request.form.get('description')
        city = request.form.get('city')
        address = request.form.get('address')
        
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"vendor_{current_user.id}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = filename
        
        vendor = Vendor(
            user_id=current_user.id,
            business_name=business_name,
            category=category,
            description=description,
            state=state,
            city=city,
            address=address,
            image_path=image_path
        )
        db.session.add(vendor)
        db.session.commit()
        
        flash('Business listing created successfully!', 'success')
        return redirect(url_for('vendor_dashboard'))
    
    return render_template('create_vendor.html', states=INDIAN_STATES, categories=BUSINESS_CATEGORIES)

@app.route('/vendor/edit', methods=['GET', 'POST'])
@login_required
def edit_vendor():
    if current_user.role != 'vendor':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    vendor = Vendor.query.filter_by(user_id=current_user.id).first()
    if not vendor:
        return redirect(url_for('create_vendor'))
    
    if request.method == 'POST':
        state = request.form.get('state')
        
        if state not in INDIAN_STATES:
            flash('Please select a valid Indian state', 'error')
            return redirect(url_for('edit_vendor'))
        
        vendor.business_name = request.form.get('business_name')
        vendor.category = request.form.get('category')
        vendor.description = request.form.get('description')
        vendor.state = state
        vendor.city = request.form.get('city')
        vendor.address = request.form.get('address')
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"vendor_{current_user.id}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                vendor.image_path = filename
        
        db.session.commit()
        flash('Business listing updated successfully!', 'success')
        return redirect(url_for('vendor_dashboard'))
    
    return render_template('edit_vendor.html', vendor=vendor, states=INDIAN_STATES, categories=BUSINESS_CATEGORIES)

@app.route('/vendor/<int:vendor_id>')
def vendor_profile(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    
    sort_by = request.args.get('sort', 'recent')
    hygiene_filter = request.args.get('hygiene')
    staff_filter = request.args.get('staff')
    pricing_filter = request.args.get('pricing')
    necessities_filter = request.args.get('necessities')
    
    reviews = Review.query.filter_by(vendor_id=vendor_id)
    
    # Apply filters
    if hygiene_filter:
        reviews = reviews.filter(Review.hygiene_rating >= int(hygiene_filter))
    if staff_filter:
        reviews = reviews.filter(Review.staff_rating >= int(staff_filter))
    if pricing_filter:
        reviews = reviews.filter(Review.pricing_rating >= int(pricing_filter))
    if necessities_filter:
        reviews = reviews.filter_by(necessities_available=(necessities_filter == 'yes'))
    
    # Apply sorting
    if sort_by == 'highest':
        reviews = reviews.order_by(Review.overall_rating.desc())
    elif sort_by == 'lowest':
        reviews = reviews.order_by(Review.overall_rating.asc())
    else:
        reviews = reviews.order_by(Review.created_at.desc())
    
    reviews = reviews.all()
    
    # Calculate statistics
    avg_rating = db.session.query(db.func.avg(Review.overall_rating)).filter_by(vendor_id=vendor_id).scalar()
    avg_hygiene = db.session.query(db.func.avg(Review.hygiene_rating)).filter_by(vendor_id=vendor_id).scalar()
    avg_staff = db.session.query(db.func.avg(Review.staff_rating)).filter_by(vendor_id=vendor_id).scalar()
    avg_pricing = db.session.query(db.func.avg(Review.pricing_rating)).filter_by(vendor_id=vendor_id).scalar()
    necessities_yes = Review.query.filter_by(vendor_id=vendor_id, necessities_available=True).count()
    total_reviews = len(Review.query.filter_by(vendor_id=vendor_id).all())
    
    stats = {
        'avg_rating': round(avg_rating, 1) if avg_rating else 0,
        'avg_hygiene': round(avg_hygiene, 1) if avg_hygiene else 0,
        'avg_staff': round(avg_staff, 1) if avg_staff else 0,
        'avg_pricing': round(avg_pricing, 1) if avg_pricing else 0,
        'necessities_percent': round((necessities_yes / total_reviews * 100), 1) if total_reviews > 0 else 0,
        'total_reviews': total_reviews
    }
    
    return render_template('vendor_profile.html', vendor=vendor, reviews=reviews, stats=stats)

@app.route('/vendor/<int:vendor_id>/review', methods=['GET', 'POST'])
@login_required
def add_review(vendor_id):
    if current_user.role != 'customer':
        flash('Only customers can leave reviews', 'error')
        return redirect(url_for('vendor_profile', vendor_id=vendor_id))
    
    vendor = Vendor.query.get_or_404(vendor_id)
    
    if request.method == 'POST':
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"review_{current_user.id}_{vendor_id}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = filename
        
        review = Review(
            vendor_id=vendor_id,
            customer_id=current_user.id,
            hygiene_rating=int(request.form.get('hygiene_rating')),
            necessities_available=request.form.get('necessities_available') == 'yes',
            staff_rating=int(request.form.get('staff_rating')),
            pricing_rating=int(request.form.get('pricing_rating')),
            overall_rating=int(request.form.get('overall_rating')),
            text=request.form.get('text'),
            image_path=image_path
        )
        db.session.add(review)
        db.session.commit()
        
        flash('Review submitted successfully!', 'success')
        return redirect(url_for('vendor_profile', vendor_id=vendor_id))
    
    return render_template('review_form.html', vendor=vendor)


@app.route('/hygiene-guidelines')
def hygiene_guidelines():
    return render_template('hygiene_guidelines.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()