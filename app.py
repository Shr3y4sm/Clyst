# type: ignore[import]
from datetime import date
import os
from dotenv import load_dotenv
import natural_search
import ai
import uuid

# Load environment variables from .env file
load_dotenv()
from werkzeug.utils import secure_filename
from flask import Flask, abort, render_template, redirect, url_for, flash, request, jsonify, session
import json
# Type hints for better IDE support
from typing import Optional, Dict, Any, List
from flask_bootstrap5 import Bootstrap
from flask_ckeditor import CKEditor
from flask_migrate import Migrate
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
app.config['SESSION_PERMANENT'] = True
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

ckeditor = CKEditor(app)
Bootstrap(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Specify what view to redirect to when login is required
login_manager.login_message_category = 'info'  # Optional: use bootstrap info category for flash messages


# Configure Gravatar (commented out due to compatibility issues)
# gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


class Base(DeclarativeBase):
    pass


# Database configuration
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True  # Enable automatic reconnection
}

if os.getenv('FLASK_ENV') == 'production':
    # Use PostgreSQL for production (Railway, Render)
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL:
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL.replace('postgres://', 'postgresql://')
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clyst.db'
else:
    # Use SQLite for development (store DB in Flask instance folder)
    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, 'clyst.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

# Initialize SQLAlchemy with the declarative base class
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db, compare_type=True, render_as_batch=True)

# Create database tables within app context if they don't exist
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        if os.path.exists(db_path):
            os.remove(db_path)
            print("🔄 Removed corrupted database file")


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
    is_verified: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=False, server_default='0')
    verification_photo: Mapped[Optional[str]] = mapped_column(db.String(255), nullable=True)
    verification_date: Mapped[Optional[str]] = mapped_column(db.String(250), nullable=True)
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
    is_promoted: Mapped[bool] = mapped_column(db.Boolean, default=False)


class Product(db.Model):
    __tablename__ = 'products'

    product_id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    artist_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('users.id'))
    artist = relationship("User", back_populates="products")
    title: Mapped[Optional[str]] = mapped_column(db.String(150))
    description: Mapped[Optional[str]] = mapped_column(db.Text)
    price: Mapped[Optional[float]] = mapped_column(db.Numeric(10, 2))
    img_url: Mapped[Optional[str]] = mapped_column(db.String(255))
    created_at: Mapped[Optional[str]] = mapped_column(db.String(250))
    is_promoted: Mapped[bool] = mapped_column(db.Boolean, default=False)


class Comments(db.Model):
    __tablename__ = 'comments'

    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(
        db.Integer,
        db.ForeignKey('posts.post_id', ondelete='CASCADE'),
        nullable=False
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
    content = db.Column(db.Text)
    created_at: Mapped[Optional[str]] = mapped_column(db.String(250))


class PostLike(db.Model):
    __tablename__ = 'post_likes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class ProductComments(db.Model):
    __tablename__ = 'product_comments'

    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text)
    created_at: Mapped[Optional[str]] = mapped_column(db.String(250))


class Cart(db.Model):
    __tablename__ = 'carts'

    cart_id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at: Mapped[Optional[str]] = mapped_column(db.String(250))
    updated_at: Mapped[Optional[str]] = mapped_column(db.String(250))
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    item_id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    cart_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('carts.cart_id'), nullable=False)
    product_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity: Mapped[int] = mapped_column(db.Integer, default=1)
    added_at: Mapped[Optional[str]] = mapped_column(db.String(250))
    product = relationship("Product")
    cart = relationship("Cart", back_populates="items")
    added_at: Mapped[Optional[str]] = mapped_column(db.String(250))
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")


# ===== ORDER MODELS =====
class Order(db.Model):
    __tablename__ = 'orders'

    order_id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status: Mapped[str] = mapped_column(db.String(50), default='pending')  # pending, paid, shipped, delivered, canceled
    payment_status: Mapped[str] = mapped_column(db.String(50), default='unpaid')  # unpaid, paid, refunded
    payment_reference: Mapped[Optional[str]] = mapped_column(db.String(120))
    total_price: Mapped[Optional[float]] = mapped_column(db.Numeric(10, 2))
    shipping_name: Mapped[Optional[str]] = mapped_column(db.String(120))
    shipping_phone: Mapped[Optional[str]] = mapped_column(db.String(30))
    shipping_address: Mapped[Optional[str]] = mapped_column(db.Text)
    created_at: Mapped[Optional[str]] = mapped_column(db.String(250))
    updated_at: Mapped[Optional[str]] = mapped_column(db.String(250))

    user = relationship("User")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    product_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('products.product_id'), nullable=True)
    product_title: Mapped[Optional[str]] = mapped_column(db.String(200))
    product_img_url: Mapped[Optional[str]] = mapped_column(db.String(255))
    unit_price: Mapped[Optional[float]] = mapped_column(db.Numeric(10, 2))
    quantity: Mapped[int] = mapped_column(db.Integer, default=1)
    total_price: Mapped[Optional[float]] = mapped_column(db.Numeric(10, 2))

    order = relationship("Order", back_populates="items")
    product = relationship("Product")



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

    # Load comments per post and attach a simple comments list (with author info)
    for post in posts:
        comments_rows = db.session.execute(db.select(Comments).where(Comments.post_id == post.post_id)).scalars().all()
        comments_data = []
        for c in comments_rows:
            author = db.session.get(User, c.user_id)
            comments_data.append({
                'id': c.comment_id,
                'content': c.content,
                'created_at': c.created_at,
                'artist': {
                    'name': getattr(author, 'name', 'Unknown') if author else 'Unknown',
                    'email': getattr(author, 'email', '') if author else '',
                    'id': getattr(author, 'id', None) if author else None,
                }
            })
        # Attach to post object so template can use post.comments
        setattr(post, 'comments', comments_data)

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
    # Get next page from query params
    next_page = request.args.get('next')
    
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()

        if user and password and check_password_hash(user.password_hash, password):
            login_user(user)
            # Redirect to next_page if it exists and is a relative path, otherwise go home
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
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
            created_at=date.today().strftime("%B %d, %Y"),
            is_promoted=request.form.get('is_promoted') == 'True'
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home'))
    
    # Pre-fill from query parameters for promotion
    title = request.args.get('title', '')
    description = request.args.get('description', '')
    media_url = request.args.get('media_url', '')
    is_promoted = request.args.get('is_promoted', 'False')
    
    return render_template("add_posts.html", current_user=current_user, title=title, description=description, media_url=media_url, is_promoted=is_promoted)


@app.route("/promote_product/<int:product_id>", methods=["POST"])
@login_required
def promote_product(product_id):
    product = db.get_or_404(Product, product_id)
    if product.artist_id != current_user.id:
        abort(403)
    
    return redirect(url_for('add_posts', 
                            title=product.title, 
                            description=product.description, 
                            media_url=product.img_url,
                            is_promoted='True'))


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
    # Load comments for this product
    comments_rows = db.session.execute(db.select(ProductComments).where(ProductComments.product_id == product.product_id)).scalars().all()
    comments_data = []
    for c in comments_rows:
        author = db.session.get(User, c.user_id)
        comments_data.append({
            'id': c.comment_id,
            'content': c.content,
            'created_at': c.created_at,
            'artist': {
                'name': getattr(author, 'name', 'Unknown') if author else 'Unknown',
                'email': getattr(author, 'email', '') if author else '',
                'id': getattr(author, 'id', None) if author else None,
            }
        })
    setattr(product, 'comments', comments_data)
    return render_template("product_buy.html",
                           current_user=current_user,
                           product=product)


@app.route('/product/<int:product_id>/comment', methods=["POST"])
@login_required
def add_product_comment(product_id):
    content = (request.form.get('comment') or '').strip()
    if not content:
        flash('Comment cannot be empty')
        return redirect(url_for('product_buy', product_id=product_id))

    new_comment = ProductComments(
        product_id=product_id,
        user_id=current_user.id,
        content=content,
        created_at=date.today().strftime("%B %d, %Y")
    )
    db.session.add(new_comment)
    db.session.commit()
    anchor = request.form.get('anchor')
    if anchor:
        return redirect(url_for('product_buy', product_id=product_id) + '#' + anchor)
    return redirect(url_for('product_buy', product_id=product_id))


@app.route('/product/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_product_comment(comment_id):
    comment = db.get_or_404(ProductComments, comment_id)
    if comment.user_id != current_user.id and current_user.id != 1:
        abort(403)
    product_id = comment.product_id
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('product_buy', product_id=product_id) + '#product-' + str(product_id) + '-comments')


@app.route('/comment/<int:post_id>', methods=["POST"])
@login_required
def add_comments(post_id):
    """Create a comment for a given post_id. Expects form field 'comment'."""
    content = (request.form.get('comment') or '').strip()
    if not content:
        flash('Comment cannot be empty')
        return redirect(url_for('home'))

    new_comment = Comments(
        post_id=post_id,
        user_id=current_user.id,
        content=content,
        created_at=date.today().strftime("%B %d, %Y")
    )
    db.session.add(new_comment)
    db.session.commit()
    # Redirect back to the post anchor so the page doesn't jump to the top
    anchor = request.form.get('anchor')
    if anchor:
        return redirect(url_for('home') + '#' + anchor)
    return redirect(url_for('home'))


@app.route('/api/post/<int:post_id>/likes', methods=['GET'])
def get_post_likes(post_id):
    # Return total like count and whether current user liked (if authenticated)
    total = db.session.execute(db.select(PostLike).where(PostLike.post_id == post_id)).scalars().all()
    count = len(total)
    liked = False
    if current_user and getattr(current_user, 'is_authenticated', False):
        exists = db.session.execute(db.select(PostLike).where(PostLike.post_id == post_id, PostLike.user_id == current_user.id)).scalar()
        liked = bool(exists)
    return jsonify({'count': count, 'liked': liked})


@app.route('/api/post/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_post_like(post_id):
    # Toggle like: if exists, remove; otherwise add
    existing = db.session.execute(db.select(PostLike).where(PostLike.post_id == post_id, PostLike.user_id == current_user.id)).scalar()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        liked = False
    else:
        nl = PostLike(post_id=post_id, user_id=current_user.id)
        db.session.add(nl)
        db.session.commit()
        liked = True

    total = db.session.execute(db.select(PostLike).where(PostLike.post_id == post_id)).scalars().all()
    return jsonify({'count': len(total), 'liked': liked})


@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = db.get_or_404(Comments, comment_id)
    # Allow delete if the current user created it or is admin (id == 1)
    if comment.user_id != current_user.id and current_user.id != 1:
        abort(403)
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    # Redirect back to the post anchor
    return redirect(url_for('home') + '#post-' + str(post_id))


@app.route("/verify-phone", methods=["GET", "POST"])
@login_required
def verify_otp():
    """Phone verification page before camera access"""
    show_otp = False
    submitted_phone = request.form.get("phone", current_user.phone if current_user.phone else "")
    
    if request.method == "POST":
        if "otp" in request.form:
            # Verify OTP (dummy check for now)
            if request.form["otp"] == "1234":
                session["phone_verified"] = True
                flash("Phone number verified successfully!", "success")
                return redirect(url_for("camera"))
            else:
                flash("Invalid OTP. Please try again.", "error")
                show_otp = True
        else:
            # Phone number submitted, show OTP field
            show_otp = True
            flash("OTP sent! (Demo: Use 1234)", "success")
    
    return render_template("verify_otp.html", 
                         current_user=current_user, 
                         show_otp=show_otp, 
                         submitted_phone=submitted_phone)

@app.route("/camera")
@login_required
def camera():
    """Camera page for verification purposes"""
    if not session.get("phone_verified"):
        return redirect(url_for("verify_otp"))
    return render_template("camera.html", current_user=current_user)

@app.route("/complete-verification", methods=["POST"])
@login_required
def complete_verification():
    """Complete the verification process"""
    if not session.get("phone_verified"):
        return jsonify({"success": False, "message": "Phone verification required"}), 400
    
    try:
        data = request.get_json()
        if not data or "photo" not in data:
            return jsonify({"success": False, "message": "Missing required data"}), 400

        # Save the verification photo
        photo_data = data["photo"]
        if photo_data.startswith('data:image'):
            # Extract the base64 part
            photo_data = photo_data.split(',')[1]
        
        # Generate unique filename
        filename = f"verification_{current_user.id}_{uuid.uuid4().hex[:8]}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'verification', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save the image
        import base64
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(photo_data))
        
        # Update user verification status
        current_user.is_verified = True
        current_user.verification_photo = filename
        current_user.verification_date = str(date.today())
        db.session.commit()
        
        # Clear the session verification flag
        session.pop("phone_verified", None)
        
        flash("Congratulations! Your account is now verified.", "success")
        return jsonify({
            "success": True,
            "message": "Verification completed successfully",
            "redirect": url_for("profile")
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ===== CART ROUTES =====

def get_or_create_cart(user_id):
    """Get existing cart or create new one for user"""
    try:
        cart = db.session.execute(db.select(Cart).where(Cart.user_id == user_id)).scalar()
        if not cart:
            cart = Cart(
                user_id=user_id,
                created_at=date.today().strftime("%B %d, %Y"),
                updated_at=date.today().strftime("%B %d, %Y")
            )
            db.session.add(cart)
            db.session.commit()
        return cart
    except Exception as e:
        db.session.rollback()
        raise e
        db.session.commit()
    return cart


@app.route("/cart")
@login_required
def view_cart():
    """View shopping cart"""
    try:
        cart = get_or_create_cart(current_user.id)
        cart_items = db.session.execute(
            db.select(CartItem).where(CartItem.cart_id == cart.cart_id)
        ).scalars().all()

        # Filter out items with deleted/missing products
        valid_items = [item for item in cart_items if item.product is not None]

        # Optionally, remove invalid ones automatically
        invalid_items = [item for item in cart_items if item.product is None]
        for bad_item in invalid_items:
            db.session.delete(bad_item)
        if invalid_items:
            db.session.commit()

        total_price = sum(item.quantity * float(item.product.price) for item in valid_items)

        return render_template(
            "cart.html",
            current_user=current_user,
            cart_items=valid_items,
            total_price=total_price
        )
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error accessing cart: {str(e)}")
        return f"Error accessing cart: {str(e)}", 500



@app.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    """Add product to cart"""
    product = db.get_or_404(Product, product_id)
    cart = get_or_create_cart(current_user.id)
    
    # Check if product already in cart
    existing_item = db.session.execute(
        db.select(CartItem).where(
            CartItem.cart_id == cart.cart_id,
            CartItem.product_id == product_id
        )
    ).scalar()
    
    if existing_item:
        existing_item.quantity += 1
    else:
        new_item = CartItem(
            cart_id=cart.cart_id,
            product_id=product_id,
            quantity=1,
            added_at=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_item)
    
    cart.updated_at = date.today().strftime("%B %d, %Y")
    db.session.commit()
    
    return jsonify({"success": True, "message": "Product added to cart"})


@app.route("/cart/update/<int:item_id>", methods=["POST"])
@login_required
def update_cart_item(item_id):
    """Update cart item quantity"""
    item = db.get_or_404(CartItem, item_id)
    cart = db.get_or_404(Cart, item.cart_id)
    
    # Ensure user owns this cart
    if cart.user_id != current_user.id:
        abort(403)
    
    quantity = request.json.get('quantity', 1)
    if quantity <= 0:
        db.session.delete(item)
    else:
        item.quantity = quantity
    
    cart.updated_at = date.today().strftime("%B %d, %Y")
    db.session.commit()
    
    return jsonify({"success": True, "message": "Cart updated"})


@app.route("/cart/remove/<int:item_id>", methods=["POST"])
@login_required
def remove_from_cart(item_id):
    """Remove item from cart"""
    item = db.get_or_404(CartItem, item_id)
    cart = db.get_or_404(Cart, item.cart_id)
    
    # Ensure user owns this cart
    if cart.user_id != current_user.id:
        abort(403)
    
    db.session.delete(item)
    cart.updated_at = date.today().strftime("%B %d, %Y")
    db.session.commit()
    
    return jsonify({"success": True, "message": "Item removed from cart"})


@app.route("/cart/clear", methods=["POST"])
@login_required
def clear_cart():
    """Clear entire cart"""
    cart = get_or_create_cart(current_user.id)
    
    # Delete all cart items
    db.session.execute(db.delete(CartItem).where(CartItem.cart_id == cart.cart_id))
    cart.updated_at = date.today().strftime("%B %d, %Y")
    db.session.commit()
    
    return jsonify({"success": True, "message": "Cart cleared"})


@app.route("/api/cart/count")
@login_required
def get_cart_count():
    """Get cart item count for navbar"""
    cart = db.session.execute(db.select(Cart).where(Cart.user_id == current_user.id)).scalar()
    if not cart:
        return jsonify({"count": 0})
    
    count = db.session.execute(
        db.select(db.func.sum(CartItem.quantity)).where(CartItem.cart_id == cart.cart_id)
    ).scalar() or 0
    
    return jsonify({"count": count})


# ===== CHECKOUT AND ORDERS =====
@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    """Checkout page to confirm shipping details and place order.
    POST creates an order from the user's cart and clears the cart.
    """
    # Load cart and validate
    cart = get_or_create_cart(current_user.id)
    cart_items = db.session.execute(
        db.select(CartItem).where(CartItem.cart_id == cart.cart_id)
    ).scalars().all()

    # Only include valid items (products that still exist)
    valid_items = [item for item in cart_items if item.product is not None]
    if request.method == 'POST':
        if not valid_items:
            flash('Your cart is empty.', 'error')
            return redirect(url_for('view_cart'))

        # Gather shipping info from form
        shipping_name = (request.form.get('shipping_name') or current_user.name or '').strip()
        shipping_phone = (request.form.get('shipping_phone') or current_user.phone or '').strip()
        shipping_address = (request.form.get('shipping_address') or current_user.location or '').strip()

        if not shipping_name or not shipping_phone or not shipping_address:
            flash('Please provide name, phone, and address for shipping.', 'error')
            return render_template(
                'checkout.html',
                current_user=current_user,
                cart_items=valid_items,
                subtotal=sum(i.quantity * float(i.product.price) for i in valid_items),
                shipping_name=shipping_name,
                shipping_phone=shipping_phone,
                shipping_address=shipping_address
            )

        # Compute totals
        subtotal = sum(i.quantity * float(i.product.price) for i in valid_items)
        total = subtotal  # Free shipping placeholder

        # Create Order
        new_order = Order(
            user_id=current_user.id,
            status='pending',
            payment_status='unpaid',
            total_price=total,
            shipping_name=shipping_name,
            shipping_phone=shipping_phone,
            shipping_address=shipping_address,
            created_at=date.today().strftime("%B %d, %Y"),
            updated_at=date.today().strftime("%B %d, %Y"),
        )
        db.session.add(new_order)
        db.session.flush()  # get order_id

        # Add OrderItems (snapshot of current product info)
        for ci in valid_items:
            db.session.add(OrderItem(
                order_id=new_order.order_id,
                product_id=ci.product_id,
                product_title=ci.product.title,
                product_img_url=ci.product.img_url,
                unit_price=ci.product.price,
                quantity=ci.quantity,
                total_price=ci.quantity * float(ci.product.price)
            ))

        # Clear cart
        db.session.execute(db.delete(CartItem).where(CartItem.cart_id == cart.cart_id))
        cart.updated_at = date.today().strftime("%B %d, %Y")
        db.session.commit()

        # Redirect to order detail
        return redirect(url_for('order_detail', order_id=new_order.order_id))

    # GET: show checkout page populated from user/cart
    return render_template(
        'checkout.html',
        current_user=current_user,
        cart_items=valid_items,
        subtotal=sum(i.quantity * float(i.product.price) for i in valid_items),
        shipping_name=current_user.name or '',
        shipping_phone=current_user.phone or '',
        shipping_address=current_user.location or ''
    )


@app.route('/orders')
@login_required
def orders_list():
    """List current user's orders."""
    orders = db.session.execute(
        db.select(Order).where(Order.user_id == current_user.id).order_by(db.desc(Order.order_id))
    ).scalars().all()
    return render_template('orders.html', current_user=current_user, orders=orders)


@app.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id: int):
    """Order details with items and status."""
    order = db.get_or_404(Order, order_id)
    if order.user_id != current_user.id and current_user.id != 1:
        abort(403)
    # Items are loaded via relationship
    return render_template('order_detail.html', current_user=current_user, order=order)


@app.route('/orders/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id: int):
    order = db.get_or_404(Order, order_id)
    if order.user_id != current_user.id and current_user.id != 1:
        abort(403)
    if order.status in ('pending',) and order.payment_status in ('unpaid',):
        order.status = 'canceled'
        order.updated_at = date.today().strftime("%B %d, %Y")
        db.session.commit()
        flash('Order canceled.', 'info')
    else:
        flash('Order cannot be canceled at this stage.', 'error')
    return redirect(url_for('order_detail', order_id=order_id))


@app.route('/admin/orders/<int:order_id>/status', methods=['POST'])
@admin_only
def admin_update_order_status(order_id: int):
    """Admin endpoint to update order and payment status. Expects form fields 'status' and optional 'payment_status'."""
    order = db.get_or_404(Order, order_id)
    status = (request.form.get('status') or '').strip().lower()
    payment_status = (request.form.get('payment_status') or '').strip().lower()
    allowed_status = {'pending', 'paid', 'shipped', 'delivered', 'canceled'}
    allowed_pay = {'', 'unpaid', 'paid', 'refunded'}
    if status and status in allowed_status:
        order.status = status
    if payment_status in allowed_pay and payment_status:
        order.payment_status = payment_status
    order.updated_at = date.today().strftime("%B %d, %Y")
    db.session.commit()
    flash('Order updated.', 'success')
    return redirect(url_for('order_detail', order_id=order_id))


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()  # In case error occurred during database operations
    return render_template('500.html'), 500

if __name__ == "__main__":
    try:
        # Enable debug mode by default for direct python execution
        app.debug = True
        
        # Create database tables
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Test database connection
            db.session.execute(db.select(User).limit(1))
            print("✅ Database connection test successful")

        # Run the app
        port = int(os.getenv('PORT', 5000))
        print(f"🚀 Starting app on port {port}")
        app.run(host='127.0.0.1', port=port)
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        db.session.rollback()  # Rollback any failed transactions
        print("⚠️ If you're getting database errors, try these steps:")
        print("1. Delete the instance/clyst.db file")
        print("2. Run 'flask db upgrade' to recreate the database")
        print("3. Start the app again")
        raise
