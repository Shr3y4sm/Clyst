from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
import models.dbs


class Base(DeclarativeBase):
    pass


app = Flask(__name__)

db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
db.init_app(app)


with app.app_context():
    db.create_all()


@app.route('/', methods=["GET", "POST"])
def home():
    pass
    # result = db.session.execute(db.select(Post).order_by(Post.product_name))
    # all_posts = result.scalars()
    # return render_template("index.html", posts=all_posts)


@app.route("/add", methods=["GET", "POST"])
def add():
    pass
    # if request.method == "POST":
    #     new_book = Post(
    #         product_name=request.form["product_name"],
    #         artist_name=request.form["artist_name"],
    #         price=request.form["price"]
    #     )
    #     db.session.add(new_book)
    #     db.session.commit()
    #     return redirect(url_for('home'))
    # return render_template("add.html")


@app.route("/delete")
def delete():
    pass
    # post_id = request.args.get('id')
    # post_to_delete = db.get_or_404(Post, post_id)
    # db.session.delete(post_to_delete)
    # db.session.commit()
    # return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)