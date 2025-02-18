from flask_restful import Resource
from flask import jsonify, request, current_app
from application.models import User,Songs,Albums,Album_Songs,Playlists,Playlist_songs,Ratings
import bcrypt
from flask_jwt_extended import create_access_token, get_jwt,jwt_required, get_jwt_identity
from application.models import db,User
import jwt
import os,json
from application.config import LocalDev
from werkzeug.utils import secure_filename
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz


#############################################    Token     ###########################################

class Token(Resource):
    @jwt_required()
    def get(self):
        claims=get_jwt()
        user_role=claims['role']
        email=claims['email']
        name=claims['name']
        return jsonify(user_role,email,name)

#####################################################################################################################


##########################################           Uploading         ############################################


class Uploadsong(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        email=claims['email']
        song_name=request.form.get('song_name')
        artist=request.form.get('artist')
        lyrics=request.form.get('lyrics')
        song_file=request.files['song_file']
        thumbnail=request.files['thumbnail']
        if song_name=="" or artist=="" or lyrics=="" or song_file=="" or thumbnail=="":
            return jsonify('Complete all fields')
        pathname=secure_filename(song_file.filename)
        userdetail=User.query.filter_by(email=email, active=True, role=3).first()
        if not(userdetail):
            return ('unauthorized')
        # song_file.save(os.path.join('./static/songs', pathname))
        song_file.save(os.path.join('./../frontend/src/assets/songs', pathname))

        thumb=secure_filename(thumbnail.filename)
        thumbnail.save(os.path.join('./../frontend/src/assets/images', thumb))
        pathtostore=pathname
        thumbnailtostore=thumb
        user1 = User.query.filter_by(email=email, active=True).first()
        if user1:
            if user1.role==3:
                u1 = Songs(song_name=song_name, artist=artist, lyrics=lyrics, path=pathtostore, thumbnail=thumbnailtostore, creator=user1.id, song_admin_permission=True, average_rating=0)
                db.session.add(u1)
                db.session.commit()
                print('success')
                return jsonify('success')
            else:
                print('unauthorized')
                return jsonify('unauthorized')
        return jsonify('unauthorized')    




class Uploadalbum(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        email=claims['email']
        role=claims['role']

        album_name=request.form.get('album_name')

        artist=request.form.get('artist')

        genre=request.form.get('genre')

        album_files=request.files.getlist('album_file[]')

        thumbnail=request.files['thumbnail']
        if album_name=="" or artist=="" or genre=="" or album_files=="" or thumbnail=="":
            return jsonify('Complete all fields')

        if role!=3:
            return jsonify('unauthorized')
        user1=User.query.filter_by(email=email, active=True, role=3).first()
        if not(user1):
            return jsonify('unauthorized')
        x=Albums.query.filter_by(album_name=album_name).first()
        if x:
            return jsonify('album already exists')
        user1=User.query.filter_by(email=email).first()
        creator=user1.id
        u1=Albums(album_name=album_name, artist=artist,genre=genre,album_admin_permission=True,creator=creator)

        db.session.add(u1)
        db.session.commit()
        ualbum=Albums.query.filter_by(album_name=album_name).first()

        thumb=secure_filename(thumbnail.filename)
        thumbnail.save(os.path.join('./../frontend/src/assets/images',thumb))
        for song in album_files:
            pathname=secure_filename(song.filename)
            song.save(os.path.join('./../frontend/src/assets/songs', pathname))
            u1 = Songs(song_name=pathname, artist=artist, lyrics="", path=pathname, thumbnail=thumb, creator=creator, song_admin_permission=True, average_rating=0)
            db.session.add(u1)
            db.session.commit()
            u2=Songs.query.filter_by(song_name=pathname).first()
            u3=Album_Songs(song_id=u2.id, album_id=ualbum.album_id)
            db.session.add(u3)
            db.session.commit()
        print('success')
        return jsonify('success')

#####################################################################################################################




################################################  Login And Signup #####################################################


class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if email=="" or password =="":
            return jsonify('Email or password cannot be empty')
        
        
        user1 = User.query.filter_by(email=email).first()

        # bcrypt.checkpw(password.encode('utf-8'), u1.password)
        if not user1:
            return jsonify('User not exist')
        elif not bcrypt.checkpw(password.encode('utf-8'), user1.password):
            return jsonify('Incorrect password')
        else:
            user1.login_time = datetime.now()
            db.session.commit()
            print(user1.login_time)
            d={ "name": user1.name,
                 "email": user1.email, 
               "role": user1.role, 
               "active": user1.active}
            token=create_access_token(email, additional_claims=d)
            print('success')
            return jsonify(token=token)
            # Return token


class Signup(Resource):              #--         for user          --#
    def post(self):   
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name=data.get('name')

        if email=="" or password =="" or name=="":
            print('empty')
            return jsonify('Fill the required fields')
        
        user1 = User.query.filter_by(email=email).first()

        if not user1:
            u1 = User(name=name, email=email, password=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()), active=True, role=2, login_time=datetime.now())
            db.session.add(u1)
            db.session.commit()
            d={ "name": name,
                "email": email, 
               "role": 2, 
               "active": True}
            token=create_access_token(email, additional_claims=d)
            return jsonify(token=token)
        
        else:
            print('Email in use')
            return jsonify('Email in use')



#####################################################################################################################


#################################################### Playlists ######################################################

   

    
class Updateplaylist(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        email=claims['email']
        user1=User.query.filter_by(email=email).first()
        data=request.get_json()
        playlist_name=data.get('name')
        playlist_id=data.get('id')
        result=Playlists.query.filter_by(playlist_id=playlist_id,creator=user1.id).first()
        if result:
            result.playlist_name=playlist_name
            db.session.commit()
            return jsonify('success')
        return jsonify('unauthorized')
    

class Deleteplaylist(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        email=claims['email']
        data=request.get_json()
        playlist_id=data.get('id')
        user1=User.query.filter_by(email=email).first()
        result=Playlists.query.filter_by(playlist_id=playlist_id,creator=user1.id).first()
        if not result:
            return jsonify('unauthorized')
        result=Playlists.query.filter_by(playlist_id=playlist_id).first()
        db.session.delete(result)
        db.session.commit()
        was=Playlist_songs.query.filter_by(playlist_id=playlist_id).all()
        for i in was:
            was1=Playlist_songs.query.filter_by(playlist_id=playlist_id).first()
            db.session.delete(was1)
            db.session.commit()
        db.session.commit()
        return jsonify('success') 


class Getplaylists(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        email=claims['email']
        creator=User.query.filter_by(email=email).first()
        if not creator:
            return jsonify('unauthorized')
        result=Playlists.query.filter_by(creator=creator.id).all()
        res=[]
        for i in result:
            d={
                'playlist_id':i.playlist_id,
                'playlist_name':i.playlist_name,
                'creator':i.creator
            }
            res.append(d)   
        return jsonify(res)    
    

class Createplaylist(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        data=request.get_json()
        playlist_name=data.get('playlist_name')
        email=claims['email']
        user1=User.query.filter_by(email=email).first()
        if not user1:
            return jsonify('unauthorized')
        u1=Playlists(playlist_name=playlist_name,creator=user1.id)
        db.session.add(u1)
        db.session.commit()
        return jsonify('success')     



class Addsongtoplaylist(Resource):
    @jwt_required()
    def post(self):
        data=request.get_json()
        playlist_id=data.get('playlistId')
        song_id=data.get('songId')
        u2=Playlist_songs.query.filter_by(playlist_id=playlist_id,song_id=song_id).first()
        if u2:
            return jsonify('song already exists')
        u1=Playlist_songs(playlist_id=playlist_id,song_id=song_id)

        db.session.add(u1)
        db.session.commit()
        return jsonify('success')



class Openplaylist(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        data=request.get_json()
        playlist_id=data.get('playlist_id')
        email=claims['email']
        user=User.query.filter_by(email=email).first()
        creator=Playlists.query.filter_by(playlist_id=playlist_id,creator=user.id).first()
        if not creator:
            return jsonify('unauthorized')
        result=Playlist_songs.query.filter_by(playlist_id=playlist_id).all()
        res=[]
        for i in result:
            u1=Songs.query.filter_by(id=i.song_id, song_admin_permission=True).first()
            if u1:
                d={
                    'id':u1.id,
                    'song_name':u1.song_name,
                    'path':u1.path,
                    'thumbnail':u1.thumbnail,
                    'creator':u1.creator,
                    'artist':u1.artist,
                    'lyrics':u1.lyrics,
                    'average_rating':u1.average_rating
                }
                res.append(d)   
        return jsonify(res)  



class Deletefromplaylist(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        email=claims['email']
        data=request.get_json()
        playlist_id=data.get('playlist_id')
        song_id=data.get('song_id')
        user1=User.query.filter_by(email=email).first()
        exist=Playlists.query.filter_by(playlist_id=playlist_id,creator=user1.id).first()
        if not exist:
            return jsonify('unauthorized')
        result=Playlist_songs.query.filter_by(playlist_id=playlist_id,song_id=song_id).first()
        db.session.delete(result)
        db.session.commit()
        print('success')
        return jsonify('success')   


########################################################################################################################

#########################################      UPDATING PROFILE      ####################################################
class Becomecreator(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        token=request.get_json()
        email = claims['email']
        user1 = User.query.filter_by(email=email).first()
        user1.role=3
        db.session.commit()
        user1 = User.query.filter_by(email=email).first()
        d={
            "name": user1.name,
            "email": user1.email,
            "role": user1.role,
            "active": user1.active
        } 
        token=create_access_token(email, additional_claims=d)
        return jsonify(token=token)
    
class Updatename(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        data=request.get_json()
        name=data.get('name')
        email=claims['email']
        try:
            user1 = User.query.filter_by(email=email).first()
            user1.name=name
            db.session.commit()
            d={
                "name": user1.name,
                "email": user1.email,
                "role": user1.role,
                "active": user1.active
            }
            token=create_access_token(email, additional_claims=d)
            return jsonify(token=token)
        except Exception as e:
            print(e)
            return jsonify('error') 

class Updateemail(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        data=request.get_json()
        email=data.get('email')
        exactemail=claims['email']
        try:
            user1 = User.query.filter_by(email=exactemail).first()
            user2=User.query.filter_by(email=email).first()
            if user2:
                return jsonify('Email in use')
            user1.email=email
            db.session.commit()
            d={
                "name": user1.name,
                "email": user1.email,
                "role": user1.role,
                "active": user1.active
            }
            token=create_access_token(email, additional_claims=d)
            return jsonify(token=token)
        except Exception as e:
            return jsonify('error')         

class Updatepassword(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        data=request.get_json()
        password=data.get('password')
        email=claims['email']
        try:
            user1 = User.query.filter_by(email=email).first()
            user1.password=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
            db.session.commit()
            d={
                "name": user1.name,
                "email": user1.email,
                "role": user1.role,
                "active": user1.active
            }
            token=create_access_token(email, additional_claims=d)
            return jsonify(token=token)
        except Exception as e:
            return jsonify(e)     
        




##################################################################################################################





        
class Allsongs(Resource):
    def get(self):
        result=Songs.query.order_by(Songs.average_rating.desc()).all()
        print(result)
        songs=[]
        for i in result:
            if i.song_admin_permission==True:
                d={
                'id':i.id,
                'song_name':i.song_name,
                'path':i.path,
                'thumbnail':i.thumbnail,
                'artist':i.artist,
                'lyrics':i.lyrics,
                'song_admin_permission':i.song_admin_permission,
                'average_rating':i.average_rating,
                'creator':i.creator
                }
                songs.append(d)
        return jsonify(songs)
    
class Creatorsongs(Resource):
    @jwt_required()
    def post(self):
        data=request.get_json()
        email=data.get('email')
        creator=User.query.filter_by(email=email).first()
        result=Songs.query.filter_by(creator=creator.id, song_admin_permission=True).all()
        songs=[]
        for i in result:
            d={
                'id':i.id,
                'song_name':i.song_name,
                'path':i.path,
                'thumbnail':i.thumbnail,
                'artist':i.artist,
                'lyrics':i.lyrics,
                'song_admin_permission':i.song_admin_permission,
                'average_rating':i.average_rating,
                'creator':i.creator
            }
            songs.append(d)
        return jsonify(songs)

class Updatesongname(Resource):
    @jwt_required()
    def post(self):
        print("hitted")
        data=request.get_json()
        id=data.get('song_id')
        try:
            result=Songs.query.filter_by(id=id).first()
            result.song_name=data.get('songname')
            db.session.commit()
            return jsonify('success')
        except Exception as e:
            print(e)
            return jsonify('error')


class Deletesong(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        email=claims['email']
        data=request.get_json()
        id=data.get('id')
        creator=User.query.filter_by(email=email).first()
        usr=Songs.query.filter_by(id=id, creator=creator.id).first()
        if not usr:
            return jsonify('error')
        try:
            result=Songs.query.filter_by(id=id).first()
            db.session.delete(result)
            was=Ratings.query.filter_by(song_id=id).all()
            for i in was:
                db.session.delete(i)
                db.session.commit()
            result2=Album_Songs.query.filter_by(song_id=id).first()
            if result2:
                db.session.delete(result2)
            db.session.commit()
            res=Playlist_songs.query.filter_by(song_id=id).all()
            for i in res:
                db.session.delete(i)
                db.session.commit()
            print('success')
            return jsonify('success')
        except Exception as e:
            print(e)
            return jsonify('error')
        
class Getalbums(Resource):
    def get(self):
        result=Albums.query.filter_by(album_admin_permission=True).all()
        albums=[]
        for i in result:
            u1=Album_Songs.query.filter_by(album_id=i.album_id).first()
            u2=Songs.query.filter_by(id=u1.song_id, song_admin_permission=True).first()
            if u2:
                d={
                    'album_name':i.album_name,
                    'thumbnail' : u2.thumbnail,
                    'artist':i.artist,
                    'genre':i.genre,
                    'album_admin_permission':i.album_admin_permission,
                    'creator':i.creator
                }
                albums.append(d)    
        return jsonify(albums)
        

class Openalbum(Resource):
    def post(self):
        data=request.get_json()
        album_name=data.get('album_name')
        result=Albums.query.filter_by(album_name=album_name, album_admin_permission=True).first()
        if result:
            list=Album_Songs.query.filter_by(album_id=result.album_id).all()
            songs=[]
            for song in list:
                song1=Songs.query.filter_by(id=song.song_id, song_admin_permission=True).first()
                if song1:
                    d={
                        'id':song1.id,
                        'song_name':song1.song_name,
                        'path':song1.path,
                        'thumbnail':song1.thumbnail,
                        'artist':song1.artist,
                        'lyrics':song1.lyrics,
                        'song_admin_permission':song1.song_admin_permission,
                        'average_rating':song1.average_rating,
                        'creator':song1.creator
                    }
                    songs.append(d)    
        return jsonify(songs=songs,result=result.album_name)
    

class Creatoralbum(Resource):
    @jwt_required()
    def get(self):
        email=request.args.get('email')
        creator=User.query.filter_by(email=email).first()
        result=Albums.query.filter_by(creator=creator.id, album_admin_permission=True).all()
        print(result, creator.id)
        albums=[]
        for i in result:
            u1=Album_Songs.query.filter_by(album_id=i.album_id).first()
            if u1:
                u2=Songs.query.filter_by(id=u1.song_id, song_admin_permission=True).first()
                if u2:
                    d={
                        'album_name':i.album_name,
                        'artist':i.artist,
                        'thumbnail':u2.thumbnail,
                        'genre':i.genre,
                        'album_admin_permission':i.album_admin_permission,
                        'creator':i.creator
                    }
                    albums.append(d)  
            print(albums)      
        return jsonify(albums=albums)
    


class Updatealbumname(Resource):
    @jwt_required()
    def post(self):
        data=request.get_json()
        # {'name': 'mallu', 'album_name': 'giyan'}
        toupdate=data.get('name')
        album_name=data.get('album_name')
        res=Albums.query.filter_by(album_name=toupdate).first()
        if res:
            return jsonify('album already exists')
        try:
            result=Albums.query.filter_by(album_name=album_name).first()
            result.album_name=toupdate
            db.session.commit()
            print('success')
            return jsonify('success')
        except Exception as e:
            print(e)
            return jsonify('error')    
        

class Deletealbum(Resource):
    @jwt_required()
    def post(self):
        data=request.get_json()
        album_name=data.get('album_name')
        result=Albums.query.filter_by(album_name=album_name).first()
        db.session.delete(result)
        db.session.commit()
        songs=Album_Songs.query.filter_by(album_id=result.album_id).all()
        for i in songs:
            was=Playlist_songs.query.filter_by(song_id=i.song_id).all()
            for j in was:
                db.session.delete(j)
                db.session.commit()
        for i in songs:
            was=Album_Songs.query.filter_by(song_id=i.song_id).first()
            db.session.delete(was)
            db.session.commit()
            song=Songs.query.filter_by(id=i.song_id).first()
            db.session.delete(song)
            db.session.commit()
        for i in songs:
            was=Ratings.query.filter_by(song_id=i.song_id).all()
            for j in was:
                db.session.delete(j)
                db.session.commit()    
        for i in songs:
            db.session.delete(i)
            db.session.commit() 

        db.session.commit()

        print('success')
        return jsonify('success')
    
 


class Search(Resource):
    def post(self):
        data=request.get_json()
        query=data.get('query')
        result=Songs.query.filter((Songs.song_name.like('%'+query+'%'))|(Songs.artist.like('%'+query+'%'))).all()
        print(result)
        res=[]
        for i in result:
            if i.song_admin_permission==True:
                d={
                    'id':i.id,
                    'song_name':i.song_name,
                    'path':i.path,
                    'thumbnail':i.thumbnail,
                    'creator':i.creator,
                    'artist':i.artist,
                    'lyrics':i.lyrics,
                    'average_rating':i.average_rating
                }
                res.append(d)
        print('success',res)
        return jsonify(res)
    

class Updaterating(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        data=request.get_json()
        song_id=data.get('id')
        rating=data.get('rating')
        email=claims['email']
        creator=User.query.filter_by(email=email).first()
        check=Ratings.query.filter_by(creator=creator.id,song_id=song_id).first()
        if check:
            check.rating=rating
            db.session.commit()
            result=Ratings.query.filter_by(song_id=song_id).all()
            j=0
            total=0
            for i in result:
                j=j+i.rating
                total+=1
            avg=j/total
            u1=Songs.query.filter_by(id=song_id).first()
            u1.average_rating=avg
            db.session.commit()    
            print('success')
            return jsonify(avg)
        else:
            u1=Ratings(creator=creator.id,song_id=song_id,rating=rating)
            db.session.add(u1)
            db.session.commit()
            result=Ratings.query.filter_by(song_id=song_id).all()
            j=0
            total=0
            for i in result:
                j=j+i.rating
                total+=1
            avg=j/total
            u1=Songs.query.filter_by(id=song_id).first()
            u1.average_rating=avg
            db.session.commit() 
            print('success')
            return jsonify(avg)  






###################################### ONLY ADMIN ##############################################

class Adminlogin(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if email=="" or password =="":
            print('empty')
            return jsonify('Email or password cannot be empty')
        
        user1 = User.query.filter_by(email=email,role=1).first()

        # bcrypt.checkpw(password.encode('utf-8'), u1.password)
        if not user1:
            print('user dosnt exist')
            return jsonify('User not exist')
        elif not bcrypt.checkpw(password.encode('utf-8'), user1.password):
            print('incorrect password')
            return jsonify('Incorrect password')
        else:
            d={ "name": user1.name,
                 "email": user1.email, 
               "role": user1.role, 
               "active": user1.active}
            token=create_access_token(email, additional_claims=d)
            return jsonify(token=token)          
        

class Admininfo(Resource):
    @jwt_required()
    def get(self):
        claims=get_jwt()
        role=claims['role']
        name=claims['name']
        email=claims['email']
        if role!=1:
            return jsonify('Only admin can access')
        else:
            result1=Songs.query.all()
            result2=Albums.query.all()
            result3=User.query.filter_by(role=3).all()
            result4=User.query.filter_by(role=2).all()
            print(1)
            return jsonify(totalsongs=len(result1),totalalbums=len(result2),totalcreator=len(result3),totaluser=len(result4),name=name,email=email)
        
class Adminalbums(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        role=claims['role']
        if role!=1:
            return jsonify('Only admin can access')
        else:
            result=Albums.query.all()
            res=[]
            for i in result:
                d={
                    'album_id':i.album_id,
                    'album_name':i.album_name,
                    'artist':i.artist,
                    'genre':i.genre,
                    'creator':i.creator,
                    'album_admin_permission':i.album_admin_permission
                }
                res.append(d)
            return jsonify(res) 

class Disablealbum(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        data=request.get_json()
        album_id=data.get('album_id')
        role=claims['role']
        if role!=1:
            return jsonify('Only admin can access')
        result=Albums.query.filter_by(album_id=album_id).first()
        result.album_admin_permission=False
        db.session.commit()
        Albumsongs=Album_Songs.query.filter_by(album_id=album_id).all()
        for i in Albumsongs:
            song=Songs.query.filter_by(id=i.song_id).first()
            if song:
                song.song_admin_permission=False
                db.session.commit()
        return jsonify('success')
    
class Enablealbum(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        data=request.get_json()
        album_id=data.get('album_id')
        role=claims['role']
        if role!=1:
            return jsonify('Only admin can access')
        result=Albums.query.filter_by(album_id=album_id).first()
        result.album_admin_permission=True
        db.session.commit()
        Albumsongs=Album_Songs.query.filter_by(album_id=album_id).all()
        for i in Albumsongs:
            song=Songs.query.filter_by(id=i.song_id).first()
            if song:
                song.song_admin_permission=True
                db.session.commit()
        return jsonify('success')    
    

class Allsongsbyadmin(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        role = claims['role']
        if role != 1:
            return jsonify('Only admin can access')
        else:
            result = Songs.query.all()
            res = []
            for i in result:
                d = {
                    'id': i.id,
                    'song_name': i.song_name,
                    'path': i.path,
                    'thumbnail': i.thumbnail,
                    'creator': i.creator,
                    'artist': i.artist,
                    'lyrics': i.lyrics,
                    'song_admin_permission': i.song_admin_permission,
                    'average_rating': i.average_rating
                }
                res.append(d)
            return jsonify(res)
  

class Disablesong(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        data=request.get_json()
        song_id=data.get('song_id')
        role=claims['role']
        if role!=1:
            return jsonify('Only admin can access')
        result=Songs.query.filter_by(id=song_id).first()
        result.song_admin_permission=False
        db.session.commit()
        return jsonify('success')    
    
class Enablesong(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        data=request.get_json()
        song_id=data.get('song_id')
        role=claims['role']
        if role!=1:
            return jsonify('Only admin can access')
        result=Songs.query.filter_by(id=song_id).first()
        result.song_admin_permission=True
        db.session.commit()
        return jsonify('success')    
    

class Deletealbumbyadmin(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        data=request.get_json()
        album_id=data.get('album_id')
        role=claims['role']
        if role!=1:
            return jsonify('Only admin can access')
        result=Albums.query.filter_by(album_id=album_id).first()
        db.session.delete(result)
        db.session.commit()
        songs=Album_Songs.query.filter_by(album_id=album_id).all()
        for i in songs:
            was=Playlist_songs.query.filter_by(song_id=i.song_id).all()
            for j in was:
                db.session.delete(j)
                db.session.commit()
        for i in songs:
            was=Album_Songs.query.filter_by(song_id=i.song_id).first()
            db.session.delete(was)
            db.session.commit()
            song=Songs.query.filter_by(id=i.song_id).first()
            db.session.delete(song)
            db.session.commit()
        for i in songs:
            was=Ratings.query.filter_by(song_id=i.song_id).all()
            for j in was:
                db.session.delete(j)
                db.session.commit()    
        for i in songs:
            db.session.delete(i)
            db.session.commit() 

        db.session.commit()        
        return jsonify('success')
    

class Deletesongbyadmin(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        data=request.get_json()
        song_id=data.get('song_id')
        role=claims['role']
        if role!=1:
            return jsonify('Only admin can access')
        result=Songs.query.filter_by(id=song_id).first()
        db.session.delete(result)
        db.session.commit()
        was=Playlist_songs.query.filter_by(song_id=song_id).all()
        for i in was:
            db.session.delete(i)
            db.session.commit()
        result2=Album_Songs.query.filter_by(song_id=song_id).all()
        for i in result2:
            db.session.delete(i)
            db.session.commit()
        result3=Ratings.query.filter_by(song_id=song_id).all()
        for i in result3:
            db.session.delete(i)
            db.session.commit()    
        return jsonify('success')    
    

class Admincreators(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        role=claims['role']
        if role!=1:
            return jsonify('Only admin can access')
        res=User.query.filter_by(role=3).all()
        result=[]
        for i in res:
            d={
                'email':i.email,
                'name':i.name,
                'role':i.role,
                'creator_id':i.id,
                'active':i.active
            }
            result.append(d)

        return jsonify(result)
    

class Disablecreator(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        data=request.get_json()
        creator_id=data.get('creator_id')
        role=claims['role']
        if role!=1:
            return jsonify('Only admin can access')
        result=User.query.filter_by(id=creator_id).first()
        result.active=False
        db.session.commit()
        return jsonify('success')
    
class Enablecreator(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        data=request.get_json()
        creator_id=data.get('creator_id')
        role=claims['role']
        if role!=1:
            return jsonify('Only admin can access')
        result=User.query.filter_by(id=creator_id).first()
        result.active=True
        db.session.commit()
        return jsonify('success') 


class Adminusers(Resource):
    @jwt_required()
    def get(self):
        claims =get_jwt()
        role=claims['role']
        if role!=1:
            return jsonify('Only admin can access')
        res=User.query.filter_by(role=2).all()
        result=[]
        for i in res:
            d={
                'email':i.email,
                'name':i.name,
                'role':i.role,
                'user_id':i.id,
                'active':i.active
            }
            result.append(d)
        return jsonify(result) 

class Disableuser(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        data=request.get_json()
        user_id=data.get('user_id')
        role=claims['role']
        if role!=1:
            return jsonify('Only admin can access')
        result=User.query.filter_by(id=user_id).first()
        result.active=False
        db.session.commit()
        return jsonify('success')
    

class Enableuser(Resource):
    @jwt_required()
    def post(self):
        claims=get_jwt()
        data=request.get_json()
        user_id=data.get('user_id')
        role=claims['role']
        if role!=1:
            return jsonify('Only admin can access')
        result=User.query.filter_by(id=user_id).first()
        result.active=True
        db.session.commit()
        return jsonify('success') 

class Adminvisuals(Resource):
    @jwt_required()
    def get(self):
        claims =get_jwt()
        role=claims['role']
        if role != 1:
            return jsonify('Only admin can access')
        
        # Get counts for categories
        users = len(User.query.filter_by(role=2).all())   
        creators = len(User.query.filter_by(role=3).all())
        songs = len(Songs.query.all())
        albums = len(Albums.query.all())
        
        categories = ['Users', 'Creators', 'Songs', 'Albums']
        values = [users, creators, songs, albums]
        plt.clf()
        # Save the first plot
        pathname = 'visuals1.png'
        save_path1 = os.path.join('./../frontend/src/assets', pathname)

        with current_app.app_context():
            plt.bar(categories, values)
            plt.xlabel('Categories')
            plt.ylabel('Count')
            plt.title('Distribution')

            if os.path.exists(save_path1):
                os.remove(save_path1)
            plt.savefig(save_path1)
            plt.clf()


        star5=len(Songs.query.filter_by(average_rating=5).all())
        star4=len(Songs.query.filter_by(average_rating=4).all())
        star3=len(Songs.query.filter_by(average_rating=3).all())
        star2=len(Songs.query.filter_by(average_rating=2).all())
        star1=len(Songs.query.filter_by(average_rating=1).all())
        unrated=len(Songs.query.filter_by(average_rating=0).all())

        categories=['5 star', '4 star', '3 star', '2 star', '1 star', 'Unrated']
        values=[star5, star4, star3, star2, star1, unrated]

        pathname='visuals5.png'
        save_path5=os.path.join('./../frontend/src/assets', pathname)

        with current_app.app_context():
            plt.bar(categories, values)
            plt.xlabel('Rating')
            plt.ylabel('Count')
            plt.title(' Songs Rating distribution')

            if os.path.exists(save_path5):
                os.remove(save_path5)
            plt.savefig(save_path5)
            plt.clf()


        # Get counts for albums and songs per album
        albums_data = Albums.query.all()
        album_counts = []
        song_counts = []
        for album in albums_data:
            album_songs = Album_Songs.query.filter_by(album_id=album.album_id).all()
            song_counts.append(len(album_songs))
            album_counts.append(album.album_name)
        
        # Save the second plot
        pathname = 'visuals2.png'
        save_path2 = os.path.join('./../frontend/src/assets', pathname)

        with current_app.app_context():
            plt.bar(album_counts, song_counts)
            plt.xlabel('Albums')
            plt.ylabel('Count')
            plt.title('Albums distribution')

            for i in range(len(album_counts)):
                plt.text(album_counts[i], song_counts[i], str(song_counts[i]), ha='center', va='bottom')

            if os.path.exists(save_path2):
                os.remove(save_path2)
            plt.savefig(save_path2)    
            plt.clf()

        # Get counts for blacklisted and whitelisted songs
        blacklistedsongs = len(Songs.query.filter_by(song_admin_permission=False).all())
        whitelistedsongs = len(Songs.query.filter_by(song_admin_permission=True).all())

        # Save the third plot (pie chart)
        pathname = 'visuals3.png'
        save_path3 = os.path.join('./../frontend/src/assets', pathname)

        with current_app.app_context():
            labels = ['Blacklisted', 'Whitelisted']
            sizes = [blacklistedsongs, whitelistedsongs]
            colors = ['#ff9999', '#66b3ff']
            explode = (0.1, 0)  # explode 1st slice (i.e., 'Blacklisted')

            plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
            plt.title('Distribution of Blacklisted and Whitelisted Songs')

            if os.path.exists(save_path3):
                os.remove(save_path3)
            plt.savefig(save_path3)
            plt.clf()

        blacklistedusers=len(User.query.filter_by(active=False).all())
        whitelistedusers=len(User.query.filter_by(active=True).all())

        pathname = 'visuals4.png'
        save_path4 = os.path.join('./../frontend/src/assets', pathname)

        with current_app.app_context():
            labels = ['Blacklisted', 'Whitelisted']
            sizes = [blacklistedusers, whitelistedusers]
            colors = ['#ff9999', '#66b3ff']
            explode = (0.1, 0)  # explode 1st slice (i.e., 'Blacklisted')

            plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
            plt.title('Distribution of Blacklisted and Whitelisted Users')

            if os.path.exists(save_path4):
                os.remove(save_path4)
            plt.savefig(save_path4)
            plt.clf()

        return jsonify({'image_path': save_path1, 'image_path2': save_path2, 'image_path3': save_path3})
    



    
