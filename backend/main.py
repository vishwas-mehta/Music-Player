from flask import Flask, jsonify
from application.models import db, User,Songs,Albums
from application.config import LocalDev
from flask_restful import Resource, Api
from application.api import Login,Signup,Becomecreator,Updateemail,Updatename,Updatepassword,Uploadsong,Allsongs,Creatorsongs,Updatesongname,Deletesong,Uploadalbum,Getalbums,Openalbum,Creatoralbum,Updatealbumname,Deletealbum,Createplaylist,Getplaylists,Updateplaylist,Deleteplaylist,Addsongtoplaylist,Openplaylist,Deletefromplaylist,Search,Updaterating,Adminlogin,Admininfo,Adminalbums,Enablealbum,Disablealbum,Disablesong,Enablesong,Deletealbumbyadmin,Deletesongbyadmin,Admincreators,Disablecreator,Enablecreator,Adminusers,Disableuser,Enableuser,Adminvisuals,Token,Allsongsbyadmin
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from celery import Celery
from flask_mail import Mail, Message
from celery.schedules import crontab
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os



app = None
api = None

def create_app():
    
    app=Flask(__name__)

    app.config.from_object(LocalDev)

    
    #models.py and db.sqlite3 to be coionected
    # app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.sqlite3'

    #Models.py and main.py connrcted
    db.init_app(app)   # to connect db object to app db object === app
    app.app_context().push()  # to modify database 
   # security ko app se connect

    api=Api(app)


    

    return app, api


app, api=create_app()



CORS(app)
jwt=JWTManager(app)


######################################################### Mailing and Celery tasks ##################################



app.config['MAIL_SERVER']='localhost'
app.config['MAIL_PORT'] = 1025   #Mailing SMIP port
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = None
app.config['MAIL_PASSWORD'] = None
app.config['MAIL_DEFAULT_SENDER'] = 'itunes@email.com'

mail=Mail(app)


celery=Celery(app.name, broker="redis://localhost:6379/0", backend="redis://localhost:6379/1", broker_connection_retry_on_startup = True)

celery.conf.beat_schedule = {
    'send-mail-every-5-seconds': {
        'task': 'main.dailyreminderstousers',
        'schedule': timedelta(seconds=20),
    },
    'send-mail-monthly': {
        'task': 'main.monthlreport',
        'schedule': timedelta(seconds=20)
    }
}





# celery.conf.beat_schedule = {
#     'send-mail-every-day': {
#         'task': 'main.dailyreminderstousers',
#         'schedule': crontab(hour=15, minute=00),
#     },
#     'send-mail-monthly': {
#         'task': 'main.monthlreport',
#         'schedule': crontab(hour=15, minute=00, day_of_month=1),
#     }
# }



@celery.task
def dailyreminderstousers():
    with app.app_context():
        timedecided=datetime.now()-timedelta(seconds=1)
        users=User.query.all()
        for i in users:
            if i.role!=1:
                if i.login_time<=timedecided:
                    recipient_email=i.email
                    subject="Exciting Songs Are Waiting for You"
                    message="Hello Good Evening "+i.name+". Greetings from Itunes App. Your account has been inactive for more than 24 hours. Please visit itunes.com to reactivate your account. Thank you."
                    msg=Message(subject, sender='itunes@email.com', recipients=[recipient_email])
                    msg.body=message
                    mail.send(msg)
                    print("Reminder send to", recipient_email)



@celery.task
def monthlreport():
    with app.app_context():
        users = User.query.filter_by(role=3).all()
        for i in users:
            message = f"Hello {i.name}. Greetings from Itunes App. Here is your monthly report. You can find the document in the attached file. Thank you. Team Itunes"
            pdfmsg = "The Albums Created By You Are:\n"
            albums = Albums.query.filter_by(creator=i.id).all()
            for j in albums:
                pdfmsg += f"Name: {j.album_name}\tArtist: {j.artist}\tGenre: {j.genre}\n"

            pdfmsg += "\nThe Songs Created By You Are:\n"
            songs = Songs.query.filter_by(creator=i.id).all()
            for k in songs:
                pdfmsg += f"Name: {k.song_name}\tRating: {k.average_rating}\tArtist: {k.artist}\n"

            filename = f"{i.id}_report.pdf"  # Adjust filename based on user ID or any unique identifier
            generate_pdf(filename, "Monthly Report", pdfmsg)

            with open(filename, "rb") as pdf_file:
                pdf_data = pdf_file.read()
                msg = Message("Monthly Report", sender='itunes@email.com', recipients=[i.email])
                msg.body = message
                msg.attach(filename, "application/pdf", pdf_data)
                mail.send(msg)
                print("Report sent to", i.email)

def generate_pdf(filename, subject, message):
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(100, 750, subject)
    
    # Format the message with proper line breaks
    formatted_message = format_message(message)
    
    # Draw the formatted message on the canvas
    y_position = 700
    for line in formatted_message:
        c.drawString(100, y_position, line)
        y_position -= 20  # Move to the next line
    c.save()

def format_message(message):
    # Split the message into lines based on '\n' and '\t' characters
    lines = message.split('\n')
    formatted_lines = []
    for line in lines:
        # Split each line based on '\t' to separate columns
        columns = line.split('\t')
        formatted_line = ''
        for col in columns:
            formatted_line += col.strip() + '  '  # Add a space between columns
        formatted_lines.append(formatted_line.strip())  # Remove leading/trailing spaces
    return formatted_lines
 


######################################################################################################################



############################################# API ROUTES ##################################################################



api.add_resource(Login, '/login') # return token hitted by post request 
api.add_resource(Signup, '/signup')
api.add_resource(Becomecreator, '/becomecreator')
api.add_resource(Updateemail, '/updateemail')
api.add_resource(Updatename, '/updatename')
api.add_resource(Updatepassword, '/updatepassword')
api.add_resource(Uploadsong, '/uploadsong')
api.add_resource(Allsongs, '/allsongs')
api.add_resource(Creatorsongs, '/creatorsongs')
api.add_resource(Updatesongname, '/updatesongname')
api.add_resource(Deletesong, '/deletesong')
api.add_resource(Uploadalbum, '/uploadalbum')
api.add_resource(Getalbums, '/getalbums')
api.add_resource(Openalbum, '/openalbum')
api.add_resource(Creatoralbum, '/creatoralbum')
api.add_resource(Updatealbumname, '/updatealbumname')
api.add_resource(Deletealbum, '/deletealbum')
api.add_resource(Createplaylist, '/createplaylist')
api.add_resource(Getplaylists, '/getplaylists')
api.add_resource(Updateplaylist, '/updateplaylist')
api.add_resource(Deleteplaylist, '/deleteplaylist')
api.add_resource(Addsongtoplaylist, '/addsongtoplaylist')
api.add_resource(Openplaylist, '/openplaylist')
api.add_resource(Deletefromplaylist, '/deletefromplaylist')
api.add_resource(Search, '/search')
api.add_resource(Updaterating, '/updaterating')
api.add_resource(Adminlogin, '/adminlogin')
api.add_resource(Admininfo, '/admininfo')
api.add_resource(Adminalbums, '/adminalbums')
api.add_resource(Enablealbum, '/enablealbum')
api.add_resource(Disablealbum, '/disablealbum')
api.add_resource(Disablesong, '/disablesong')
api.add_resource(Enablesong, '/enablesong')
api.add_resource(Deletealbumbyadmin, '/deletealbumbyadmin')
api.add_resource(Deletesongbyadmin, '/deletesongbyadmin')
api.add_resource(Admincreators, '/admincreators')
api.add_resource(Disablecreator, '/disablecreator')
api.add_resource(Enablecreator, '/enablecreator')
api.add_resource(Adminusers, '/adminusers')
api.add_resource(Disableuser, '/disableuser')
api.add_resource(Enableuser, '/enableuser')
api.add_resource(Adminvisuals, '/adminvisuals')
api.add_resource(Token, '/token')
api.add_resource(Allsongsbyadmin, '/allsongsbyadmin')


#####################################################################################################################################



if __name__=='__main__':
    app.run(debug=True,port=5000)