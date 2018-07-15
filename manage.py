from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from redis import *
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db



app = create_app('dev')  # db=SQLAlchemy(app)


manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)



if __name__ == '__main__':
    manager.run()