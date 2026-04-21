from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import data

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///favorites.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# =====================
# MODEL
# =====================

class Favorite(db.Model):
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20))  # youtube / movie / tv


# =====================
# ROUTES
# =====================

@app.route('/')
def index():
    page_number = request.args.get("page", 1, type=int)
    movies = data.popularMovies(page_number)
    return render_template('index.html', content=movies, page=page_number)


@app.route('/series')
def series():
    page_number = request.args.get("page", 1, type=int)
    series = data.popularSeries(page_number)
    return render_template('index.html', content=series, page=page_number)


@app.route('/youtube', methods=["GET", "POST"])
def youtube():
    if request.method == "POST":
        query = request.form.get("query")
        content = data.searchYoutube(query)
    else:
        content = data.youtubeVideosByCategory()

    return render_template("youtube.html", content=content)

@app.route("/youtube/refresh")
def refresh_youtube():
    content = data.youtubeVideosByCategory(force_refresh=True)
    return redirect("/youtube")

@app.route('/search', methods=['GET', 'POST'])
def searching():
    if request.method == 'POST':
        name = request.form.get('name')
        content = data.search(name)
        return render_template('search.html', content=content)

    return render_template('search.html')

@app.route('/watch')
def watch():
    content = request.args.get("contentId")
    type_ = request.args.get("type")
    id_ = request.args.get("id")

    info = []

    if type_ == "tv" and id_:
        info = data.seriesInfo(id_)

    return render_template(
        "watch.html",
        content=content,
        type=type_,
        info=info,
        id=id_
    )


@app.route('/watching', methods=['POST'])
def watching():
    link = request.form.get('link')
    content_type = request.form.get('type')
    content_id = request.form.get('id')
    
    print(link)
    print(content_id)

    if content_type == "tv":
        content_id = content_id.replace("tv_", "")
        info = data.seriesInfo(content_id)
    elif content_type == "movie":
        content_id = content_id.replace("movie_", "")
    else:
        info = []

    return render_template('watch.html', content=link, info=info, id=content_id, type=content_type)


@app.route('/favorite', methods=['POST'])
def favorite():
    try:
        fav = Favorite(
            id=request.form.get('id'),
            title=request.form.get('title'),
            image_url=request.form.get('image'),
            link=request.form.get('link')
        )

        db.session.add(fav)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()

    return "Ok"


@app.route('/favorites')
def favorites():
    all_favorites = Favorite.query.all()
    return render_template('favorites.html', favorites=all_favorites)

@app.route('/save', methods=['POST'])
def save():
    data = request.get_json()

    unique_id = f"{data['type']}_{data['id']}"

    item = Favorite(
        id=unique_id,
        title=data['title'],
        image_url=data['image'],
        link=data['link'],
        type=data['type']
    )

    try:
        db.session.add(item)
        db.session.commit()
        return {"status": "saved"}
    except:
        db.session.rollback()
        return {"status": "exists"}

@app.route('/remove', methods=['POST'])
def remove():
    data = request.get_json()

    unique_id = f"{data['type']}_{data['id']}"

    item = Favorite.query.get(unique_id)

    if item:
        db.session.delete(item)
        db.session.commit()

    return {"status": "removed"}
# =====================
# RUN
# =====================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)