from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap5 import Bootstrap
from flask_ckeditor import CKEditor
# from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
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


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    location = db.Column(db.String(150))
    created_at = db.Column(db.String(250))
    posts = relationship("Posts", back_populates="artist")
    products = relationship("Product", back_populates="artist")


class Posts(db.Model):
    __tablename__ = 'posts'

    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    artist = relationship("User", back_populates="posts")
    post_title = db.Column(db.String(255))
    description = db.Column(db.Text)
    media_url = db.Column(db.String(255))
    created_at = db.Column(db.String(255))


class Product(db.Model):
    __tablename__ = 'products'

    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    artist = relationship("User", back_populates="products")
    title = db.Column(db.String(150))
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2))
    img_url = db.Column(db.String(255))
    # category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id', ondelete='SET NULL'))
    created_at = db.Column(db.String(250))


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
        
        if user and check_password_hash(user.password_hash, password):
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
        new_post = Posts(
            post_title=request.form['post_title'],
            description=request.form['description'],
            created_at=date.today().strftime("%B %d, %Y"),
            artist_id=current_user.id
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
        return redirect(url_for('products_page'))
    return render_template("add_products.html", current_user=current_user)


@app.route("/delete")
@login_required
@admin_only
def delete_posts():
    post_id = request.args.get('post_id')
    post_to_delete = db.get_or_404(Posts, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/delete_products")
@login_required
@admin_only
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
