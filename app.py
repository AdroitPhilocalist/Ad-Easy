from flask import Flask
app=None
def init_app():
    myapp=Flask(__name__)
    myapp.debug=True
    myapp.app_context().push()
    return myapp

app=init_app()
from backend.controller import *

if __name__=="__main__":
    app.run()