#!/usr/bin/python3
"""test for db storage"""
import unittest
import pep8
import json
import os
from models.base_model import BaseModel
from models.user import User
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.place import Place
from models.review import Review
from models import storage
from models.engine.db_storage import DBStorage


class TestDBStorage(unittest.TestCase):
    '''this will test the DBStorage'''

    def setUp(self):
        """Setup method"""
        if os.getenv('HBNB_TYPE_STORAGE') != 'db':
            self.skipTest("Using file storage")

    def test_pep8_DB_Storage(self):
        """Tests pep8 style"""
        style = pep8.StyleGuide(quiet=True)
        p = style.check_files(['models/engine/db_storage.py'])
        self.assertEqual(p.total_errors, 0, "fix pep8")

    def test_all(self):
        """tests if all works in database Storage"""
        obj = storage.all()
        self.assertEqual(type(obj), dict)

    def test_all_class(self):
        """tests if all with class works in database Storage"""
        storage.new(State(name='Hawaii'))
        objs = storage.all()
        u_objs = storage.all('User')
        self.assertIsNotNone(objs)
        self.assertEqual(type(objs), dict)
        self.assertEqual(type(u_objs), dict)
        self.assertEqual(objs, storage.all())
        self.assertNotEqual(u_objs, storage.all())
        self.assertNotEqual(objs, u_objs)

    def test_delete(self):
        """Tests if database deletion works"""
        u = User(email="Ya", password="lal", first_name="Hello",
                 last_name="Good bye")
        key = 'User' + '.' + u.id
        objs = storage.all()
        self.assertNotIn(key, objs)
        storage.new(u)
        storage.save()
        objs = storage.all()
        self.assertIn(key, objs)
        storage.delete(u)
        objs = storage.all()
        self.assertNotIn(key, objs)

    def test_new(self):
        """test when new is called"""
        obj = storage.all()
        s = State(name='New York')
        self.assertIsNone(storage.new(s))

    def test_save(self):
        """test when save is called"""
        obj = storage.all()
        s = State(name='Nevada')
        storage.new(s)
        self.assertIsNone(storage.save())

    def test_reload_db(self):
        """Test DBStorage reload does not error out
        """
        self.assertIsNone(storage.reload())

if __name__ == "__main__":
    unittest.main()
