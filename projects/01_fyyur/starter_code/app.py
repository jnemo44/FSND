#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct
import logging
from datetime import datetime
from collections import Counter
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
#connect to a local postgresql database
app.config.from_object('config')
db = SQLAlchemy(app)

#Control schema changes
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120),unique=True)
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    #artists = db.relationship('Show', back_populates='venue')
    #Relationship is one to many (Venue can host many shows)
    show_ven = db.relationship('Show', backref='venue', lazy=True)
    #Implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    #venues = db.relationship('Show', back_populates='artist')
    #Relationship is one to many (Artist can play at many shows)
    show_art = db.relationship('Show', backref='artist', lazy=True)
    def __repr__(self):
        return f'<Aritst {self.id} {self.name}>'
    #Implement any missing fields, as a database migration using Flask-Migrate

#Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'),nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    #venue = db.relationship('Venue', back_populates='artists')
    #venue = db.relationship(Venue, backref=backref("Show", cascade="all"))
    #artist = db.relationship('Artist', back_populates='venues')
    #artist = db.relationship(Artist, backref=backref("Show", cascade="all")
    
    def __repr__(self):
        return '<Show {}{}>'.format(self.artist_id, self.venue_id)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]
  
  data1= [] 
  ven_local = {}
  #Loop through distinct cities grouped by states results in unique city/state combo
  for x in db.session.query(distinct(Venue.city),Venue.state).group_by(Venue.state,Venue.city).all():
    ven_info = {}
    ven_list = []
    ven_local['city'] = x[0]
    ven_local['state'] = x[1]
    #Add all venues associated with each city/state
    for ven in db.session.query(Venue.id,Venue.name).filter(Venue.city==x[0],Venue.state==x[1]).all():
      #Build secondary dict
      ven_info['id'] = ven[0]
      ven_info['name'] = ven[1]
      ven_list.append(ven_info.copy())
    #Add venue list to the dict
    ven_local['venues'] = ven_list

    #Store venue info in a list
    data1.append(ven_local.copy())

  #city =[]
  #no_venues = []
  #Finds number of venues in each city
  #for v in areas.values(): 
  #  city.append(list(Counter(v).keys()))
  #  no_venues.append(list(Counter(v).values()))

  return render_template('pages/venues.html', areas=data1)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  #Implement search on venues with partial string search.
  #Init data structures
  response1={}
  search_results = {}
  data=[]
  #Build query
  search = request.form.get('search_term', '')
  venue_query = db.session.query(Venue.id,Venue.name).filter(Venue.name.ilike('%'+ search +'%')).all()
  for ven in venue_query:
    search_results['id']=ven[0]
    search_results['name']=ven[1]
    data.append(search_results.copy())

  #Store searched venue data inside respond
  response1["count"] = len(venue_query)
  response1["data"] = data

  return render_template('pages/search_venues.html', results=response1, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
  data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }

  #Shows the venue page with the given venue_id
  #Dict to store query retrieved
  selected_venue={}

  #Query for the selected venue
  for venue in db.session.query(Venue).filter_by(id = venue_id).all():
    selected_venue = venue.__dict__

  #Append string of Generes into a list
  genres = selected_venue['genres']
  genres_list=['']
  i = 0
  for char in genres:
    if char == "{" or char == "}":
      continue
    elif char == ",":
      i+=1
      genres_list.append('')
    else:
      genres_list[i] = genres_list[i] + char

  #Replace string data with new list
  selected_venue['genres'] = genres_list
  show_info = {}
  upcoming_shows = []
  past_shows = []
  now = datetime.now()
  #Look for upcoming shows 
  for show in db.session.query(Show.artist_id,Show.start_time).filter(Show.venue_id == selected_venue['id']).all():
    show_info["artist_id"] = show[0]
    show_info["artist_name"] = db.session.query(Artist.name).filter(Artist.id==show[0]).first()[0]
    show_info["start_time"] = str(show[1])
    if now > show[1]:
      #Show is in the past
      past_shows.append(show_info.copy())
    else:
      #Show is upcoming
      upcoming_shows.append(show_info.copy())

  selected_venue["past_shows"] = past_shows
  selected_venue["past_shows_count"] = len(past_shows)
  selected_venue["upcoming_shows"] = upcoming_shows
  selected_venue["upcoming_shows_count"] = len(upcoming_shows)

  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=selected_venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  #Insert form data as a new Venue record in the db, instead
  error = False
  data = request.form
  vname = data['name']
  vcity = data['city']
  vstate = data['state']
  vaddress = data['address']
  vphone = data['phone']
  vgenres = data.getlist('genres')
  vfb_link = data['facebook_link']
  vweb_link = data['website_link']
  if 'seeking_talent' not in data:
    vtalent = False
  else:
    vtalent = True
  vdescription = data['seeking_description']
  #vimage_link = data['image_link']
  try:
      db.session.add(Venue(
        city=vcity,
        state=vstate,
        name=vname,
        address=vaddress,
        phone=vphone,
        facebook_link=vfb_link,
        genres=vgenres,
        seeking_talent=vtalent,
        seeking_description=vdescription,
        website=vweb_link,
        #image_link=vimage_link
      ))
  except:
      error = True
  finally:
      if not error:
          db.session.commit()
          flash('Venue ' + vname +
                ' was successfully listed!')
      else:
          flash('An error occurred. Venue ' +
                vname + ' could not be listed.')
          db.session.rollback()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    if not error:
      print('no error')
      flash('Venue succesfully deleted')
    else:
      print('error')
      flash('An error occurred. Venue could not be deleted.')
    db.session.close()
  #Not redirecting. Error 405 method not allowed even though delete is working  
  return jsonify({'success': True})
  #return redirect(url_for('venues'))
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]
  #Replace with real data returned from querying the database
  artists = db.session.query(Artist.id,Artist.name).all()

  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  #Implement search on artists with partial string search. 
  #Init data structures
  response1={}
  search_results = {}
  data=[]
  #Build query
  search = request.form.get('search_term', '')
  artist_query = db.session.query(Artist.id,Artist.name).filter(Artist.name.ilike('%'+ search +'%')).all()
  for artist in artist_query:
    search_results['id']=artist[0]
    search_results['name']=artist[1]
    data.append(search_results.copy())

  #Store searched artist data inside respond
  response1["count"] = len(artist_query)
  response1["data"] = data
  
  #Return results
  return render_template('pages/search_artists.html', results=response1, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }
 
  #Replace with real venue data from the venues table, using venue_id
  #Dict to store query results
  selected_artist={}

  #Query for the selected artist (Is there a way to do this without for loop?)
  for artist in db.session.query(Artist).filter_by(id = artist_id).all():
    selected_artist = artist.__dict__

  #Append string of Generes into a list
  genres = selected_artist['genres']
  genres_list=['']
  i = 0
  for char in genres:
    if char == "{" or char == "}":
      continue
    elif char == ",":
      i+=1
      genres_list.append('')
    else:
      genres_list[i] = genres_list[i] + char

  #Replace string data with new list
  selected_artist['genres'] = genres_list

  show_info = {}
  upcoming_shows = []
  past_shows = []
  now = datetime.now()
  #Look for upcoming shows 
  for show in db.session.query(Show.venue_id,Show.start_time).filter(Show.artist_id == selected_artist['id']).all():
    show_info["venue_id"] = show[0]
    show_info["venue_name"] = db.session.query(Venue.name).filter(Venue.id==show[0]).first()[0]
    show_info["start_time"] = str(show[1])
    if now > show[1]:
      #Show is in the past
      past_shows.append(show_info.copy())
    else:
      #Show is upcoming
      upcoming_shows.append(show_info.copy())

  selected_artist["past_shows"] = past_shows
  selected_artist["past_shows_count"] = len(past_shows)
  selected_artist["upcoming_shows"] = upcoming_shows
  selected_artist["upcoming_shows_count"] = len(upcoming_shows)

  #data = list(filter(lambda d: d['id'] == artist_id, [data1,data2,data3] ))[0]
  return render_template('pages/show_artist.html', artist=selected_artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # Insert form data as a new Venue record in the db, instead
  error = False
  data = request.form
  #if data.validate_on_submit():
  aname = data['name']
  acity = data['city']
  astate = data['state']
  aphone = data['phone']
  agenres = data.getlist('genres')
  afb_link = data['facebook_link']
  adescription = data['seeking_description']
  if 'seeking_venue' not in data:
    avenue = False
  else:
    avenue = True
  try:
    db.session.add(Artist(name=aname,
    city=acity,
    state=astate,
    phone=aphone,
    genres=agenres,
    facebook_link=afb_link,
    seeking_venue=avenue,
    seeking_description=adescription,
    ))
  except:
    error=True
  finally:
    if not error:
      db.session.commit()
      flash('Artist ' + aname +
            ' was successfully listed!')
    else:
      flash('An error occurred. Artist ' +
            aname + ' could not be listed.')
      db.session.rollback()
  #else:
  #  flask('Venue ' + request.form['name'] + ' failed due to validation error!')
  return render_template('pages/home.html')
  

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]

  #Replace with real venues data.
  #num_shows should be aggregated based on number of upcoming shows per venue.
  #Query Shows table
  data1=[]
  show_info = {}
  shows = db.session.query(Show.artist_id,Show.venue_id,Show.start_time).all()
  print(shows)
  for show in shows:
    #Build Dict
    show_info["artist_id"] = show[0] 
    show_info["artist_name"] = db.session.query(Artist.name).filter(Artist.id==show[0]).first()[0]
    show_info["venue_id"] = show[1]
    show_info["venue_name"] = db.session.query(Venue.name).filter(Venue.id==show[1]).first()[0]
    show_info["start_time"] = str(show[2])
    data1.append(show_info.copy())

  return render_template('pages/shows.html', shows=data1)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  #Insert form data as a new Show record in the db, instead
  error = False
  data = request.form
  s_artist = data['artist_id']
  s_venue = data['venue_id']
  s_time = data['start_time']
  try:
    db.session.add(Show(artist_id=s_artist,
    venue_id=s_venue,
    start_time=s_time,
    ))
  except:
    error=True
  finally:
    if not error:
      db.session.commit()
      #On successful db insert, flash success.
      flash('Show was successfully listed!')
    else:
      #On unsuccessful db insert, flash an error instead.
      flash('An error occurred. Show could not be listed!')
      db.session.rollback()

  
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
  app.debug = True
  app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
