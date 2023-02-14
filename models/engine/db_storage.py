#!/usr/bin/python3
"""New database storage engine"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os
from models.base_model import BaseModel, Base
from models.city import City
from models.state import State
from models.amenity import Amenity
from models.place import Place
from models.user import User
from models.review import Review

'''Accessing and storing environment variables'''
database = os.getenv("HBNB_MYSQL_DB")
user = os.getenv("HBNB_MYSQL_USER")
host = os.getenv("HBNB_MYSQL_HOST")
passwd = os.getenv("HBNB_MYSQL_PWD")
class_dict = {"User": User, "State": State, "City": City, "Place": Place,
              "Amenity": Amenity, "Review": Review}


class DBStorage():
    """New database storage class"""
    __engine = None
    __session = None

    def __init__(self):
        """Method to create the new engine"""
        self.__engine = create_engine("mysql+mysqldb://{}:{}@{}/{}".format(
            user, passwd, host, database), pool_pre_ping=True)
        if os.getenv("HBNB_ENV") == "test":
            Base.metadata.drop_all(bind=self.__engine)

    def all(self, cls=None):
        """Method to query for all objects of optional given class name.
        Return value is a dict like FileStorage
        """
        new_dict = {}
        if cls:
            '''only queries for one class name'''
            if cls not in class_dict:
                return new_dict
            for objs in self.__session.query(class_dict[cls]).all():
                key = str(objs.__class__.__name__) + '.' + str(objs.id)
                new_dict[key] = objs
        else:
            '''loops through all current classes and queries for each'''
            for classes in class_dict.values():
                for objs in self.__session.query(classes).all():
                    key = str(classes.__name__) + '.' + str(objs.id)
                    new_dict[key] = objs
        return new_dict

    def new(self, obj):
        '''Adds the object given as an argument to the current db session'''
        self.__session.add(obj)

    def save(self):
        '''Saves the changes to the current db session'''
        self.__session.commit()

    def delete(self, obj=None):
        '''Deletes the obj given (if not none) from the current db session'''
        if obj:
            self.__session.delete(obj)

    def reload(self):
        '''Creates current db session with sessionmaker'''
        Base.metadata.create_all(bind=self.__engine)
        Session = sessionmaker(bind=self.__engine,
                               expire_on_commit=False)
        scpd_sess = scoped_session(Session)
        if self.__session is not None:
            self.__session.close()
        self.__session = scpd_sess()
