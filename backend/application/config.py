# class LocalDev():
#     debug = True
#     SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'

#     SECRET_KEY = 'SECRTKEY'                     # session creation and cookie creation
#     SECURITY_PASSWORD_HASH = 'bcrypt'           # passoward encryption type
#     SECURITY_PASSWORD_SALT = 'SUPPER SECRTER'   # for password encryption
#     SECURITY_REGISTERABLE = True                # new user can be created

import os
class LocalDev():
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'
    UPLOAD_FOLDER='uploads'

    JWT_SECRET_KEY = 'abracadabra'  
              
    # session creation and cookie creation
    # SECURITY_PASSWORD_HASH = 'bcrypt'           # passoward encryption type
    # SECURITY_PASSWORD_SALT = 'SUPPER SECRTER'   # for password encryption
    # SECURITY_REGISTERABLE = True                # new user can be created
    # SECURITY_SEND_REGISTER_EMAIL = False        # reminder cannot be send
