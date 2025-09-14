from datetime import date
import os
import uuid
from werkzeug.utils import secure_filename
from flask import Flask, abort, render_template, redirect, url_for, flash, request, jsonify
import base64
import mimetypes
import json
import requests
try:
    import google.generativeai as genai
except Exception:
    genai = None

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
@admin_only
def home():
    result = db.session.execute(db.select(Posts))
    all_posts = result.scalars().all()
    return render_template("index.html", posts=all_posts, current_user=current_user)


@app.route("/products", methods=["GET", "POST"])
@admin_only
def products():
    result = db.session.execute(db.select(Product))
    products = result.scalars().all()
    return render_template("products.html", products=products, current_user=current_user)


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
@admin_only
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
        
        # Create new post
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
    return render_template("add_posts.html", posts=Posts, current_user=current_user)


@app.route("/add_products", methods=["GET", "POST"])
@login_required
@admin_only
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
        
        # Create new product
        new_product = Product(
            artist_id=current_user.id,
            title=request.form['product_name'],
            description=request.form.get('description', ''),
            price=request.form['price'],
            img_url=request.form.get('product_image', ''),
            created_at=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('products'))
    return render_template("add_products.html", current_user=current_user)


@app.route('/api/generate_copy', methods=['POST'])
@login_required
def generate_copy():
    """
    Lightweight stub endpoint to generate title/description suggestions
    based on provided prompt/description and optional image url/base64.
    This can be replaced with a real AI provider.
    """
    try:
        data = request.get_json(silent=True) or {}
        content_type = (data.get('type') or 'post').lower()
        prompt = (data.get('prompt') or '').strip()
        description = (data.get('description') or '').strip()
        image_url = (data.get('image_url') or '').strip()
        image_base64 = data.get('image_base64')
        image_mime = data.get('image_mime')
        image_present = bool(image_url or image_base64)

        # Require image presence for generation to align with UX
        if not image_present:
            return jsonify({
                'ok': False,
                'error': 'Image is required (URL or file) to generate suggestions.'
            }), 400

        # If Gemini is configured, use it; otherwise fallback to simple stub
        api_key = GEMINI_API_KEY
        if genai and api_key and api_key != "your_gemini_api_key_here":
            try:
                genai.configure(api_key=api_key)  # type: ignore
                # Encourage variation and ask for JSON output directly
                model = genai.GenerativeModel(  # type: ignore
                    model_name='gemini-1.5-flash',
                    generation_config={
                        'temperature': 0.9,
                        'top_p': 0.95,
                        'response_mime_type': 'application/json'
                    }
                )

                # Prepare image bytes
                image_part = None
                if image_base64:
                    try:
                        image_bytes = base64.b64decode(image_base64)
                        mime_type = image_mime or 'image/jpeg'
                        image_part = {
                            'mime_type': mime_type,
                            'data': image_bytes
                        }
                    except Exception:
                        image_part = None
                elif image_url:
                    try:
                        # Best-effort fetch; limit size
                        resp = requests.get(image_url, timeout=10)
                        resp.raise_for_status()
                        content = resp.content
                        # Basic size guard (16MB already enforced server-wide)
                        mime_type = resp.headers.get('Content-Type') or mimetypes.guess_type(image_url)[0] or 'image/jpeg'
                        image_part = {
                            'mime_type': mime_type,
                            'data': content
                        }
                    except Exception:
                        image_part = None

                user_goal = 'product listing' if content_type == 'product' else 'social post'
                guidance = prompt or ''
                base_text = description or ''
                instruction = (
                    "You are a creative copy assistant for artists. "
                    f"Given an artwork image and optional context for a {user_goal}, "
                    "generate exactly 3 varied suggestions as strict JSON array under key suggestions, "
                    "each item with keys 'title' and 'description'. Keep titles under 60 chars; descriptions under 280 chars. "
                    "Return ONLY JSON with shape: {\"suggestions\":[{\"title\":\"...\",\"description\":\"...\"}, ...]}"
                )

                # Put image first to ground the response in the artwork
                parts: List[Any] = []
                if image_part:
                    parts.append(image_part)
                parts.append(instruction)
                if guidance:
                    parts.append(f"Prompt: {guidance}")
                if base_text:
                    parts.append(f"Context: {base_text}")

                result = model.generate_content(parts)

                # Robustly extract text
                text = ''
                try:
                    text = (getattr(result, 'text', '') or '').strip()
                except Exception:
                    text = ''
                if not text:
                    try:
                        for cand in getattr(result, 'candidates', []) or []:  # type: ignore[attr-defined]
                            content = getattr(cand, 'content', None)
                            for p in getattr(content, 'parts', []) or []:
                                pt = getattr(p, 'text', None)
                                if pt:
                                    text += str(pt)
                        text = text.strip()
                    except Exception:
                        text = ''
                suggestions = []
                try:
                    # If extra text surrounds JSON, isolate the outermost JSON object
                    candidate = text
                    if '{' in text and '}' in text:
                        candidate = text[text.find('{'): text.rfind('}') + 1]
                    parsed = json.loads(candidate)
                    for item in (parsed.get('suggestions') or [])[:3]:
                        title = str(item.get('title', '')).strip()
                        desc = str(item.get('description', '')).strip()
                        if title and desc:
                            suggestions.append({'title': title, 'description': desc})
                except Exception:
                    # Fallback: derive multiple variants from lines
                    lines = [ln.strip('- •\t ') for ln in (text or '').split('\n') if ln.strip()]
                    if lines:
                        for i, ln in enumerate(lines[:3]):
                            suggestions.append({
                                'title': (ln[:60] or 'Artwork Suggestion'),
                                'description': (ln[:280] or 'A unique piece blending technique and emotion.')
                            })

                if not suggestions:
                    # Final fallback simple templates
                    base_context = (prompt or description or 'artwork').strip() or 'artwork'
                    is_product = content_type == 'product'
                    titles = [
                        f"{base_context.capitalize()}: A Visual Story",
                        f"{base_context.capitalize()} — Limited Edition",
                        f"The Essence of {base_context.capitalize()}"
                    ]
                    descs = [
                        "Handcrafted piece with meticulous detail.",
                        "Original work. Premium materials, gallery-ready finish.",
                        "Expressive composition. Ships safely, ready to display."
                    ] if is_product else [
                        "An exploration through texture, light, and color.",
                        "Captures movement and mood with layered technique.",
                        "A contemplative blend of technique and emotion."
                    ]
                    suggestions = [{ 'title': titles[i], 'description': descs[i]} for i in range(3)]

                return jsonify({'ok': True, 'suggestions': suggestions})
            except Exception as e:
                return jsonify({'ok': False, 'error': f'Gemini error: {str(e)}'}), 500

        # Fallback stub generation when Gemini not configured
        base_context = (prompt or description or 'artwork').strip() or 'artwork'
        titles = [
            f"{base_context.capitalize()}: A Visual Story",
            f"{base_context.capitalize()} — Limited Edition",
            f"The Essence of {base_context.capitalize()}"
        ]
        is_product = content_type == 'product'
        descriptions = [
            "Handcrafted piece with meticulous detail.",
            "Original work. Premium materials, gallery-ready finish.",
            "Expressive composition. Ships safely, ready to display."
        ] if is_product else [
            "An exploration through texture, light, and color.",
            "Captures movement and mood with layered technique.",
            "A contemplative blend of technique and emotion."
        ]
        suggestions = [{'title': titles[i], 'description': descriptions[i]} for i in range(3)]
        return jsonify({'ok': True, 'suggestions': suggestions})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route("/delete")
@login_required
@admin_only
def delete_posts():
    post_id = request.args.get('id')
    post_to_delete = db.get_or_404(Posts, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/delete_products")
@login_required
@admin_only
def delete_products():
    product_id = request.args.get('id')
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
    
    return render_template("profile.html", 
                         user=current_user, 
                         posts=user_posts, 
                         products=user_products)


@app.route("/profile/<int:user_id>")
@admin_only
def view_profile(user_id):
    # Get user's posts and products for public profile view
    user = db.get_or_404(User, user_id)
    user_posts = db.session.execute(db.select(Posts).where(Posts.artist_id == user_id)).scalars().all()
    user_products = db.session.execute(db.select(Product).where(Product.artist_id == user_id)).scalars().all()
    
    return render_template("profile.html", 
                         current_user=current_user, 
                         profile_user=user,
                         posts=user_posts, 
                         products=user_products)


@app.route("/product/<int:product_id>")
@admin_only
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
