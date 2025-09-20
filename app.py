# type: ignore[import]
from datetime import date
import os
import natural_search 
import ai
import uuid
from werkzeug.utils import secure_filename
from flask import Flask, abort, render_template, redirect, url_for, flash, request, jsonify
import json
# Type hints for better IDE support
from typing import Optional, Dict, Any, List
from flask_bootstrap5 import Bootstrap
from flask_ckeditor import CKEditor
# from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='static')
# Load configuration from config.py
try:
    from config import GEMINI_API_KEY, FLASK_SECRET_KEY
except ImportError:
    GEMINI_API_KEY = None
    FLASK_SECRET_KEY = 'dev-secret-key-change-in-production'
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

ckeditor = CKEditor(app)
Bootstrap(app)

# Configure Flask-Login
login_manager = LoginManager()  
login_manager.init_app(app)

# Configure Gravatar (commented out due to compatibility issues)
# gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clyst.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Database creation will be done at the end


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file, folder_name):
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Create folder if it doesn't exist
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        # Save file
        file_path = os.path.join(folder_path, unique_filename)
        file.save(file_path)
        
        # Return URL path for database storage
        url_path = f"/static/uploads/{folder_name}/{unique_filename}"
        return url_path
    return None

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    name: Mapped[Optional[str]] = mapped_column(db.String(100))
    email: Mapped[Optional[str]] = mapped_column(db.String(100), unique=True)
    password_hash: Mapped[Optional[str]] = mapped_column(db.String(255))
    phone: Mapped[Optional[str]] = mapped_column(db.String(20))
    location: Mapped[Optional[str]] = mapped_column(db.String(150))
    created_at: Mapped[Optional[str]] = mapped_column(db.String(250))
    posts = relationship("Posts", back_populates="artist")
    products = relationship("Product", back_populates="artist")


class Posts(db.Model):
    __tablename__ = 'posts'

    post_id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    artist_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('users.id'))
    artist = relationship("User", back_populates="posts")
    post_title: Mapped[Optional[str]] = mapped_column(db.String(255))
    description: Mapped[Optional[str]] = mapped_column(db.Text)
    media_url: Mapped[Optional[str]] = mapped_column(db.String(255))
    created_at: Mapped[Optional[str]] = mapped_column(db.String(255))


class Product(db.Model):
    __tablename__ = 'products'

    product_id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    artist_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('users.id'))
    artist = relationship("User", back_populates="products")
    title: Mapped[Optional[str]] = mapped_column(db.String(150))
    description: Mapped[Optional[str]] = mapped_column(db.Text)
    price: Mapped[Optional[float]] = mapped_column(db.Numeric(10, 2))
    img_url: Mapped[Optional[str]] = mapped_column(db.String(255))
    # category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id', ondelete='SET NULL'))
    created_at: Mapped[Optional[str]] = mapped_column(db.String(250))


@app.route('/', methods=["GET", "POST"])
def home():
    # Optional natural language query parsing for posts
    q = (request.args.get('q') or '').strip()
    posts_query = db.select(Posts)
    if q:
        parsed = natural_search.parse_search_query(q)
        tokens = parsed.get('keywords', [])
        # Apply text filters across title/description
        joined_artist = False
        for tk in tokens:
            like = f"%{tk}%"
            if not joined_artist:
                posts_query = posts_query.join(Posts.artist)
                joined_artist = True
            posts_query = posts_query.where(
                (Posts.post_title.ilike(like)) | (Posts.description.ilike(like)) | (User.name.ilike(like))
            )
    result = db.session.execute(posts_query)
    posts = result.scalars().all()
    return render_template("index.html", posts=posts, current_user=current_user, q=q)

@app.route('/products')
def products_page():
    # Optional natural language query parsing for products
    q = (request.args.get('q') or '').strip()
    prod_query = db.select(Product)
    if q:
        parsed = natural_search.parse_search_query(q)
        tokens = parsed.get('keywords', [])
        max_price = parsed.get('max_price')
        min_price = parsed.get('min_price')
        joined_artist = False
        for tk in tokens:
            like = f"%{tk}%"
            if not joined_artist:
                prod_query = prod_query.join(Product.artist)
                joined_artist = True
            prod_query = prod_query.where(
                (Product.title.ilike(like)) | (Product.description.ilike(like)) | (User.name.ilike(like))
            )
        if max_price is not None:
            try:
                # Product.price is Numeric; cast comparison directly
                prod_query = prod_query.where(Product.price <= max_price)
            except Exception:
                pass
        if min_price is not None:
            try:
                prod_query = prod_query.where(Product.price >= min_price)
            except Exception:
                pass
    result = db.session.execute(prod_query)
    products = result.scalars().all()
    return render_template('products.html', products=products, current_user=current_user, q=q)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        
        if user and password and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password')
    
    return render_template("login.html", current_user=current_user)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        location = request.form.get('location')
        
        # Check if user already exists
        existing_user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if existing_user:
            flash('Email already registered')
            return render_template("register.html", current_user=current_user)
        
        # Create new user
        if not password:
            flash('Password is required')
            return render_template("register.html", current_user=current_user)
            
        # type: ignore[call-arg]
        new_user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            phone=phone,
            location=location,
            created_at=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('home'))
    
    return render_template("register.html", current_user=current_user)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_posts():
    if request.method == 'POST':
        # Handle image upload
        media_url = request.form.get('post_image', '')
        
        # Check if file was uploaded
        if 'post_image_file' in request.files:
            file = request.files['post_image_file']
            if file.filename != '':
                uploaded_path = save_uploaded_file(file, 'posts')
                if uploaded_path:
                    media_url = uploaded_path
        # Enforce that at least one image source is provided
        if not media_url:
            flash('Please provide an image URL or upload an image for the post.')
            return render_template("add_posts.html", current_user=current_user)
        
        # type: ignore[call-arg]
        new_post = Posts(
            artist_id=current_user.id,
            post_title=request.form['post_title'],
            description=request.form['description'],
            media_url=media_url,
            created_at=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("add_posts.html", current_user=current_user)


@app.route("/add_products", methods=["GET", "POST"])
@login_required
def add_products():
    if request.method == 'POST':
        # Handle image upload
        img_url = request.form.get('product_image', '')
        
        # Check if file was uploaded
        if 'product_image_file' in request.files:
            file = request.files['product_image_file']
            if file.filename != '':
                uploaded_path = save_uploaded_file(file, 'products')
                if uploaded_path:
                    img_url = uploaded_path
        # Enforce that at least one image source is provided
        if not img_url:
            flash('Please provide an image URL or upload an image for the product.')
            return render_template("add_products.html", current_user=current_user)
        
        # type: ignore[call-arg]
        new_product = Product(
            artist_id=current_user.id,
            title=request.form['product_name'],
            description=request.form.get('description', ''),
            price=request.form['price'],
            img_url=img_url,
            created_at=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('products_page'))
    return render_template("add_products.html", current_user=current_user)


@app.route('/api/generate_copy', methods=['POST'])
@login_required
def generate_copy():
    """
    Endpoint to generate title/description suggestions using AI.
    """
    try:
        data = request.get_json(silent=True) or {}
        content_type = data.get('type', 'post')
        prompt = data.get('prompt', '')
        description = data.get('description', '')
        image_url = data.get('image_url', '')
        image_base64 = data.get('image_base64')
        image_mime = data.get('image_mime')

        # Call AI function
        result = ai.generate_copy_suggestions(
            content_type=content_type,
            prompt=prompt,
            description=description,
            image_url=image_url,
            image_base64=image_base64,
            image_mime=image_mime,
            api_key=GEMINI_API_KEY
        )

        if result['ok']:
            return jsonify(result)
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/translate_listing', methods=['POST'])
@login_required
def translate_listing():
    """
    Translate a listing's title/description into a target language and suggest SEO phrases.
    """
    try:
        data = request.get_json(silent=True) or {}
        content_type = data.get('type', 'post')
        title = data.get('title', '')
        description = data.get('description', '')
        target_lang = data.get('target_lang', '')
        locale = data.get('locale', '')
        source_lang = data.get('source_lang', '')

        # Call AI function
        result = ai.translate_listing(
            content_type=content_type,
            title=title,
            description=description,
            target_lang=target_lang,
            locale=locale,
            source_lang=source_lang,
            api_key=GEMINI_API_KEY
        )

        if result['ok']:
            return jsonify(result)
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route("/delete_post")
@login_required
def delete_posts():
    post_id = request.args.get('post_id')
    post_to_delete = db.get_or_404(Posts, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/delete_product")
@login_required
def delete_products():
    product_id = request.args.get('product_id')
    product_to_delete = db.get_or_404(Product, product_id)
    db.session.delete(product_to_delete)
    db.session.commit()
    return redirect(url_for('products_page'))


@app.route("/profile")
@login_required
def profile():
    # Get current user's posts and products
    user_posts = db.session.execute(db.select(Posts).where(Posts.artist_id == current_user.id)).scalars().all()
    user_products = db.session.execute(db.select(Product).where(Product.artist_id == current_user.id)).scalars().all()
    
    # Generate portfolio narrative
    from ai import generate_enhanced_portfolio_narrative
    
    # Convert posts to dictionaries for AI analysis
    posts_data = []
    for post in user_posts:
        posts_data.append({
            'post_title': post.post_title,
            'post_description': post.description,
            'media_url': post.media_url,
            'created_at': post.created_at
        })
    
    # Convert products to dictionaries for AI analysis
    products_data = []
    for product in user_products:
        products_data.append({
            'title': product.title,
            'description': product.description,
            'price': product.price,
            'img_url': product.img_url,
            'created_at': product.created_at
        })
    
    # Generate the portfolio narrative
    portfolio_narrative = generate_enhanced_portfolio_narrative(
        artist_name=current_user.name,
        posts=posts_data,
        products=products_data,
        user_location=current_user.location
    )
    
    return render_template("profile.html", 
                         current_user=current_user,
                         profile_user=current_user, 
                         posts=user_posts, 
                         products=user_products,
                         portfolio_narrative=portfolio_narrative)


@app.route("/profile/<int:user_id>")
def view_profile(user_id):
    # Get user's posts and products for public profile view
    user = db.get_or_404(User, user_id)
    user_posts = db.session.execute(db.select(Posts).where(Posts.artist_id == user_id)).scalars().all()
    user_products = db.session.execute(db.select(Product).where(Product.artist_id == user_id)).scalars().all()
    
    # Generate portfolio narrative
    from ai import generate_enhanced_portfolio_narrative
    
    # Convert posts to dictionaries for AI analysis
    posts_data = []
    for post in user_posts:
        posts_data.append({
            'post_title': post.post_title,
            'post_description': post.description,
            'media_url': post.media_url,
            'created_at': post.created_at
        })
    
    # Convert products to dictionaries for AI analysis
    products_data = []
    for product in user_products:
        products_data.append({
            'title': product.title,
            'description': product.description,
            'price': product.price,
            'img_url': product.img_url,
            'created_at': product.created_at
        })
    
    # Generate the portfolio narrative
    portfolio_narrative = generate_enhanced_portfolio_narrative(
        artist_name=user.name,
        posts=posts_data,
        products=products_data,
        user_location=user.location
    )
    
    return render_template("profile.html", 
                         current_user=current_user, 
                         profile_user=user,
                         posts=user_posts, 
                         products=user_products,
                         portfolio_narrative=portfolio_narrative)


@app.route("/product/<int:product_id>")
def product_buy(product_id):
    product = db.get_or_404(Product, product_id)
    return render_template("product_buy.html", 
                         current_user=current_user, 
                         product=product)


if __name__ == "__main__":
    # Create database tables
    with app.app_context():
        db.create_all()
    app.run(debug=True)