from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    role = db.Column(db.Integer, nullable=False)
    login_time = db.Column(db.DateTime, nullable=True)    


class Songs(db.Model):
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    song_name=db.Column(db.String(255), nullable=False)
    path=db.Column(db.String(255), nullable=False)
    thumbnail=db.Column(db.String(255), nullable=True)
    artist=db.Column(db.String(255), nullable=True)
    lyrics=db.Column(db.String(255), nullable=True)
    song_admin_permission=db.Column(db.Boolean, nullable=False)
    average_rating=db.Column(db.Integer, nullable=False)
    creator=db.Column(db.Integer, db.ForeignKey('user.id'))


class Albums(db.Model):
    album_id=db.Column(db.Integer, primary_key=True)
    
    album_name=db.Column(db.String(255), nullable=False, unique=True)
    artist=db.Column(db.String(255), nullable=True)
    genre=db.Column(db.String(255), nullable=True)
    album_admin_permission=db.Column(db.Boolean, nullable=False)
    creator=db.Column(db.Integer, db.ForeignKey('user.id'))

class Album_Songs(db.Model):
    __tablename__ = 'album_songs'  # Specify the table name

    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), primary_key=True)
    album_id = db.Column(db.Integer, db.ForeignKey('albums.album_id'), primary_key=True)


class Playlists(db.Model):
    playlist_id=db.Column(db.Integer, primary_key=True)
    playlist_name=db.Column(db.String(255), nullable=False)
    creator=db.Column(db.Integer, db.ForeignKey('user.id'))

class Playlist_songs (db.Model):
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.playlist_id'),primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), primary_key=True)

class Ratings(db.Model):
    rating_id=db.Column(db.Integer, primary_key=True)
    song_id=db.Column(db.Integer, db.ForeignKey('songs.id'))
    rating=db.Column(db.Integer, nullable=True)
    creator=db.Column(db.Integer, db.ForeignKey('user.id'))




