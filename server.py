from flask import Flask, jsonify
from flask import render_template
from flask import request, send_file
import data
from data import popularMovies, popularSeries, search, seriesInfo
import json
from flask_sqlalchemy import SQLAlchemy
import random
import ast
from sqlalchemy.exc import IntegrityError




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///favorites.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    
def convert_string_to_list(string):
    try:
        # Use ast.literal_eval to safely parse the string
        result = ast.literal_eval(string)
        if isinstance(result, list):
            return result
        else:
            raise ValueError("The string does not contain a list.")
    except (ValueError, SyntaxError) as e:
        print(f"Error converting string to list: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        page_number = int(request.form.get('page'))
        new_movies = popularMovies(page_number)
    else:
        page_number = 1
        # Initial movie list rendering
        new_movies = popularMovies(page_number)

    return render_template('index.html', movies=new_movies, page_number=page_number)

@app.route('/series', methods=['GET', 'POST'])
def series():
    if request.method == 'POST':
        page_number = int(request.form.get('page'))
        new_movies = popularSeries(page_number)
    else:
        page_number = 1
        # Initial movie list rendering
        new_movies = popularSeries(page_number)

    return render_template('index.html', movies=new_movies, page_number=page_number)

@app.route('/search', methods=['GET', 'POST'])
def searching():
    if request.method == 'POST':
        name = request.form.get('name')
        content = search(name)
        return render_template('search.html', content=content)
    
    return render_template('search.html')

@app.route('/favorite', methods=['GET', 'POST'])
def loving():
    try:
        item = request.form.get('love')
        res = convert_string_to_list(item)
        print(res[3])
        title = res[0]
        image = res[1]
        link = res [2]
        id = res[3]
        show = {"id": id, "title":title, "image_url":image, "link":link}
        favorite = Favorite(id=show['id'], title=show['title'], image_url=show['image_url'], link=show['link'])
        db.session.add(favorite)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()  # Rollback the session to remove the failed insert operation
        return render_template('search.html')
    
        
    
    return render_template('search.html')

@app.route('/print_favorites')
def print_favorites():
    all_favorites = Favorite.query.all()
    for favorite in all_favorites:
        print(f"Title: {favorite.title}, Image URL: {favorite.image_url}, Link: {favorite.link}")
    return "Favorites printed to console"

@app.route('/favorites')
def favorites():
    all_favorites = Favorite.query.all()
    return render_template('favorites.html', favorites=all_favorites)
  
@app.route('/watching', methods=['POST'])
def watching():
  if request.method == 'POST':
    content = request.form.get('contentId')
    id = request.form.get('tmdb')
    type = request.form.get('type')
    print(type)
    if(type == "tv"):
      info = seriesInfo(id)
    else:
      info = [0, 0, 0]
  else:
    content = 1
  return render_template('watch.html', content = content, info = info, nEps = 0, id = id)

@app.route('/episodes', methods=['POST'])
def episodes():
  if request.method ==  'POST':
    season = request.form.get('eNumber')
    id = request.form.get('id')
    eps = int(season[4])
    season = int(season[1])
    content = request.form.get('content')
    info = seriesInfo(id)
    print(eps)
  else:
    season = 1
    
  return render_template('watch.html', nEps = eps, info = info, content = content, id = id, season = season)

@app.route('/watchepisode', methods=['POST'])
def watchEp():
  if request.method ==  'POST':
    season = request.form.get('season')
    id = request.form.get('id')
    episode = request.form.get('episodeWatch')
    print(episode)
    content = f"https://vidsrc.to/embed/tv/{id}/{season}/{episode}"
    info = seriesInfo(id)
    print(content)
  else:
    season = 1
    
  return render_template('watch.html', nEps=0, info = info, content = content, id = id, season = season)



if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run()


