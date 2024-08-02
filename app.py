from flask import Flask
from backend.models import *
app=None
def init_app():
    myapp=Flask(__name__)
    myapp.debug=True
    myapp.app_context().push()
    myapp.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///adeasy.sqlite3"
    
    
    db.init_app(myapp)
    return myapp

app=init_app()
from backend.controller import *

if __name__=="__main__":
    app.run()