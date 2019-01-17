from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from flask import current_app
import datetime

db = SQLAlchemy()

class BaseModel(db.Model):
    """Base data model for all objects"""
    __abstract__ = True

    __hide_column = '_sa_instance_state'

    def __repr__(self):
        """Define a base way to print models"""
        return '%s(%s)' % (self.__class__.__name__, {
            column: value if not isinstance(value, datetime.datetime)
                          else value.strftime(current_app.config['DATETIME_FORMAT'])
                          for column, value in self.__dict__.items() if column != self.__hide_column
        })

    def json(self):
        """
                Define a base way to jsonify models, dealing with datetime objects
        """
        return {
            column: value if not isinstance(value, datetime.datetime)
                          else value.strftime(current_app.config['DATETIME_FORMAT'])
                          for column, value in self.__dict__.items() if column != self.__hide_column
        }

class Profile(BaseModel, db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    data = db.Column(JSON)
    created_at = db.Column(db.DateTime, server_default=db.func.statement_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.statement_timestamp(),
                                        onupdate=db.func.statement_timestamp())
