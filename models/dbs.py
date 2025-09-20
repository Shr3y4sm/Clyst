# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import event
# from sqlalchemy.engine import Engine
# import enum
# from datetime import datetime
#
# db = SQLAlchemy()
#
#
# @event.listens_for(Engine, "connect")
# def enable_foreign_keys(dbapi_connection, connection_record):
#     cursor = dbapi_connection.cursor()
#     cursor.execute("PRAGMA foreign_keys=ON")
#     cursor.close()
#
#
# class UserStatus(enum.Enum):
#     ARTIST = 'artist'
#     BUYER = 'buyer'
#     ADMIN = 'admin'
#
#
# class TagStatus(enum.Enum):
#     BLACK = 'black'
#     BLUE = 'blue'
#     RED = 'red'
#     ORANGE = 'orange'
#     GREEN = 'green'
#
#
# class SuggestionStatus(enum.Enum):
#     PRICING = 'pricing'
#     DESCRIPTION = 'description'
#     PROMOTION = 'promotion'
#
#
# class AdminStatus(enum.Enum):
#     SUPER_ADMIN = 'super_admin'
#     MODERATOR = 'moderator'
#
#
# class PaymentMethod(enum.Enum):
#     CARD = 'credit_card'
#     UPI = 'upi'
#     PAYPAL = 'paypal'
#     CASH = 'cash'
#
#
# class TransactionStatus(enum.Enum):
#     SUCCESS = 'success'
#     FAILED = 'failed'
#     PENDING = 'pending'
#
#
# class User(db.Model):
#     __bind_key__ = '01'
#     __table_name__ = 'users'
#
#     user_id: db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name: db.Column(db.String(100))
#     email: db.Column(db.String(100), unique=True)
#     password_hash: db.Column(db.String(255))
#     role: db.Column(db.Enum(UserStatus, name='user_status'))
#     phone: db.Column(db.String(20))
#     location: db.Column(db.String(150))
#     created_at: db.Column(db.DateTime, default=datetime.utcnow)
#
#
# class Artists(db.Model):
#     __bind_key__ = '02'
#     __table_name__ = 'artists'
#
#     artist_id: db.Column(db.Integer, primary_key=True, autoincrement=True)
#     user_id: db.Column(
#         db.Integer,
#         db.ForeignKey('users.user_id', ondelete='CASCADE'),
#         unique=True)
#     bio: db.Column(db.Text)
#     profile_image: db.Column(db.String(255))
#     portfolio_url: db.Column(db.String(255))
#     role: db.Column(db.Enum(TagStatus, name='tag_color'))
#     kyc_verified: db.Column(db.Boolean, default=False)
#
#
# class Product(db.Model):
#     __bind_key__ = '03'  # Adjust accordingly
#     __table_name__ = 'products'
#
#     product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     artist_id = db.Column(
#         db.Integer,
#         db.ForeignKey('artists.artist_id', ondelete='CASCADE'),
#         nullable=False
#     )
#     title = db.Column(db.String(150))
#     description = db.Column(db.Text)
#     price = db.Column(db.Numeric(10, 2))
#     category_id = db.Column(
#         db.Integer,
#         db.ForeignKey('categories.category_id', ondelete='SET NULL'),
#         nullable=True
#     )
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#
#
# class Categories(db.Model):
#     __bind_key__ = '04'
#     __table_name__ = 'categories'
#
#     category_id: db.Column(db.Integer, primary_key=True, autoincrement=True)
#     user_id: db.Column(db.String(100))
#     bio: db.Column(db.Text)
#
#
# class Orders(db.Model):
#     __bind_key__ = '05'
#     __table_name__ = 'orders'
#
#     order_item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     order_id = db.Column(
#         db.Integer,
#         db.ForeignKey('orders.order_id', ondelete='CASCADE'),
#         nullable=False
#     )
#     product_id = db.Column(
#         db.Integer,
#         db.ForeignKey('products.product_id'),
#         nullable=False
#     )
#     quantity = db.Column(db.Integer)
#     price = db.Column(db.Numeric(10, 2))
#     user_id = db.Column(
#         db.Integer,
#         db.ForeignKey('users.user_id', ondelete='CASCADE'),
#         nullable=False
#     )
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#
#
# class OrderItem(db.Model):
#     __bind_key__ = '06'
#     __table_name__ = 'order_items'
#
#     order_item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     order_id = db.Column(
#         db.Integer,
#         db.ForeignKey('orders.order_id', ondelete='CASCADE'),
#         nullable=False
#     )
#     product_id = db.Column(
#         db.Integer,
#         db.ForeignKey('products.product_id'),
#         nullable=False
#     )
#     quantity = db.Column(db.Integer)
#     price = db.Column(db.Numeric(10, 2))
#
#
# class Posts(db.Model):
#     __bind_key__ = '07'
#     __table_name__ = 'posts'
#
#     post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     artist_id = db.Column(
#         db.Integer,
#         db.ForeignKey('artists.artist_id'),
#         nullable=False
#     )
#     post_title = db.Column(db.String(255))
#     description = db.Column(db.Text)
#     media_url = db.Column(db.String(255))
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#
#
# class Comments(db.Model):
#     __bind_key__ = '08'
#     __table_name__ = 'comments'
#
#     comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     post_id = db.Column(
#         db.Integer,
#         db.ForeignKey('posts.post_id', ondelete='CASCADE'),
#         nullable=False
#     )
#     user_id = db.Column(
#         db.Integer,
#         db.ForeignKey('users.user_id'),
#         nullable=False
#     )
#     content = db.Column(db.Text)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#
#
# class Reviews(db.Model):
#     __bind_key__ = '09'
#     __table_name__ = 'reviews'
#
#     review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     product_id = db.Column(
#         db.Integer,
#         db.ForeignKey('products.product_id'),
#         nullable=False
#     )
#     user_id = db.Column(
#         db.Integer,
#         db.ForeignKey('users.user_id'),
#         nullable=False
#     )
#     rating = db.Column(db.Integer)
#     comment = db.Column(db.Text)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#
#
# class AIAssistance(db.Model):
#     __bind_key__ = '10'
#     __table_name__ = 'ai_assistance'
#
#     ai_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     artist_id = db.Column(
#         db.Integer,
#         db.ForeignKey('artists.artist_id'),
#         nullable=False
#     )
#     suggestion_type = db.Column(db.Enum(SuggestionStatus, name='suggestion'))
#     suggestion_text = db.Column(db.Text)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#
#
# class Admin(db.Model):
#     __bind_key__ = '11'
#     __table_name__ = 'admin'
#
#     admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     user_id = db.Column(
#         db.Integer,
#         db.ForeignKey('users.user_id', ondelete='CASCADE'),
#         unique=True,
#         nullable=False
#     )
#     role_level = db.Column(db.Enum(AdminStatus, name='admin_role_enum'))
#     permissions = db.Column(db.Text)
#
#
# class Transactions(db.Model):
#     __bind_key__ = 'db1'
#     __table_name__ = 'transactions'
#
#     transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     order_id = db.Column(
#         db.Integer,
#         db.ForeignKey('orders.order_id'),
#         nullable=False
#     )
#     payment_method = db.Column(db.Enum(PaymentMethod, name='payment_method'))
#     status = db.Column(db.Enum(TransactionStatus, name='transaction_status'))
#     amount = db.Column(db.Numeric(10, 2))
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
