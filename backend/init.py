
from application.models import db,User
from main import create_app
import bcrypt
from datetime import datetime
app=create_app()


db.create_all()  # when app has app.app_context()
db.session.commit()


# roles
# 1=user        2=creator       3=admin
#           (email, password, active, role)
users = [("name1", "u1@email.com", "p1", True, 1,)]
for u in users:
    u1 = User(name=u[0], email=u[1], password=bcrypt.hashpw(u[2].encode('utf-8'),bcrypt.gensalt()), active=u[3], role=u[4])
    db.session.add(u1)
    db.session.commit()



