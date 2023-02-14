#!/usr/bin/python3
"""test for place"""
import unittest
import os
from models.place import Place
from models.state import State
from models.user import User
from models.city import City
from models.review import Review
from models.base_model import BaseModel
import pep8
import MySQLdb
import sqlalchemy
from models import storage


class TestPlace(unittest.TestCase):
    """this will test the place class"""

    @classmethod
    def setUpClass(cls):
        """set up for test"""
        if os.getenv('HBNB_TYPE_STORAGE') == 'db':
            return
        cls.place = Place()
        cls.place = Place()
        cls.place.city_id = "1234-abcd"
        cls.place.user_id = "4321-dcba"
        cls.place.name = "Death Star"
        cls.place.description = "UNLIMITED POWER!!!!!"
        cls.place.number_rooms = 1000000
        cls.place.number_bathrooms = 1
        cls.place.max_guest = 607360
        cls.place.price_by_night = 10
        cls.place.latitude = 160.0
        cls.place.longitude = 120.0
        cls.place.amenity_ids = ["1324-lksdjkl"]

    @classmethod
    def teardown(cls):
        """at the end of the test this will tear it down"""
        del cls.place

    def setUp(self):
        """Setup method"""
        if os.getenv('HBNB_TYPE_STORAGE') == 'db':
            self.skipTest("Using db storage")

    def tearDown(self):
        """teardown"""
        try:
            os.remove("file.json")
        except Exception:
            pass

    def test_pep8_Place(self):
        """Tests pep8 style"""
        style = pep8.StyleGuide(quiet=True)
        p = style.check_files(['models/place.py'])
        self.assertEqual(p.total_errors, 0, "fix pep8")

    def test_checking_for_docstring_Place(self):
        """checking for docstrings"""
        self.assertIsNotNone(Place.__doc__)

    def test_attributes_Place(self):
        """chekcing if amenity have attributes"""
        self.assertTrue('id' in self.place.__dict__)
        self.assertTrue('created_at' in self.place.__dict__)
        self.assertTrue('updated_at' in self.place.__dict__)
        self.assertTrue('city_id' in self.place.__dict__)
        self.assertTrue('user_id' in self.place.__dict__)
        self.assertTrue('name' in self.place.__dict__)
        self.assertTrue('description' in self.place.__dict__)
        self.assertTrue('number_rooms' in self.place.__dict__)
        self.assertTrue('number_bathrooms' in self.place.__dict__)
        self.assertTrue('max_guest' in self.place.__dict__)
        self.assertTrue('price_by_night' in self.place.__dict__)
        self.assertTrue('latitude' in self.place.__dict__)
        self.assertTrue('longitude' in self.place.__dict__)
        self.assertTrue('amenity_ids' in self.place.__dict__)

    def test_is_subclass_Place(self):
        """test if Place is subclass of Basemodel"""
        self.assertTrue(issubclass(self.place.__class__, BaseModel), True)

    def test_attribute_types_Place(self):
        """test attribute type for Place"""
        self.assertEqual(type(self.place.city_id), str)
        self.assertEqual(type(self.place.user_id), str)
        self.assertEqual(type(self.place.name), str)
        self.assertEqual(type(self.place.description), str)
        self.assertEqual(type(self.place.number_rooms), int)
        self.assertEqual(type(self.place.number_bathrooms), int)
        self.assertEqual(type(self.place.max_guest), int)
        self.assertEqual(type(self.place.price_by_night), int)
        self.assertEqual(type(self.place.latitude), float)
        self.assertEqual(type(self.place.longitude), float)
        self.assertEqual(type(self.place.amenity_ids), list)

    def test_save_Place(self):
        """test if the save works"""
        self.place.save()
        self.assertNotEqual(self.place.created_at, self.place.updated_at)

    def test_to_dict_Place(self):
        """test if dictionary works"""
        self.assertEqual('to_dict' in dir(self.place), True)


class TestPlaceDb(unittest.TestCase):
    """This will test the Place class on DB storage"""

    @classmethod
    def setUpClass(cls):
        """Setup for the test"""
        if os.getenv('HBNB_TYPE_STORAGE') != 'db':
            return
        s = State(name='California')
        s.save()
        cls.sid = s.id
        c = City(name='SF', state_id=cls.sid)
        c.save()
        cls.cid = c.id
        u = User(email='omg@gmail.com', password='testing')
        u.save()
        cls.uid = u.id

    def setUp(self):
        """Setup method"""
        if os.getenv('HBNB_TYPE_STORAGE') != 'db':
            self.skipTest("Using file storage")
        self.create_conn()
        self.para = {'city_id': self.cid, 'user_id': self.uid,
                     'name': 'Home', 'description': 'Something',
                     'number_rooms': 10, 'number_bathrooms': 11,
                     'max_guest': 12, 'price_by_night': 9000,
                     'latitude': 0.0, 'longitude': 1.1}

    def tearDown(self):
        """Teardown method to reload session"""
        storage.reload()
        self.cur.close()
        self.conn.close()

    def create_conn(self):
        """Setup mysqldb connection and cursor"""
        self.conn = MySQLdb.connect(host=os.getenv('HBNB_MYSQL_HOST'),
                                    port=3306,
                                    user=os.getenv('HBNB_MYSQL_USER'),
                                    passwd=os.getenv('HBNB_MYSQL_PWD'),
                                    db=os.getenv('HBNB_MYSQL_DB'),
                                    charset="utf8")

        self.cur = self.conn.cursor()

    def test_place_normal(self):
        """Test operation of saving a Place object with valid attributes"""
        p = Place(**self.para)
        p.save()
        id = p.id
        self.cur.execute("SELECT id FROM places WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])

    def test_place_cid_invalid(self):
        """Test operation of saving a Place object with invalid city_id"""
        self.para['city_id'] = 'fsdfsdfsf'
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            p = Place(**self.para)
            p.save()

    def test_place_cid_none(self):
        """Test operation of saving a Place object with no city_id"""
        del self.para['city_id']
        with self.assertRaises(sqlalchemy.exc.OperationalError):
            p = Place(**self.para)
            p.save()

    def test_place_uid_invalid(self):
        """Test operation of saving a Place object with invalid user_id"""
        self.para['user_id'] = 'fsdfsdfsf'
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            p = Place(**self.para)
            p.save()

    def test_place_uid_none(self):
        """Test operation of saving a Place object with no user_id"""
        del self.para['user_id']
        with self.assertRaises(sqlalchemy.exc.OperationalError):
            p = Place(**self.para)
            p.save()

    def test_place_name_edge(self):
        """Test operation of saving a Place object with `name` at edge of
        column constraint"""
        self.para['name'] = 'f' * 128
        p = Place(**self.para)
        p.save()
        id = p.id
        self.cur.execute("SELECT id FROM places WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])

    def test_place_name_invalid(self):
        """Test operation of saving a Place object with `name` over column
        constraint"""
        self.para['name'] = 'c' * 129
        with self.assertRaises(sqlalchemy.exc.DataError):
            p = Place(**self.para)
            p.save()

    def test_place_name_none(self):
        """Test operation of saving a Place object with no `name`"""
        del self.para['name']
        with self.assertRaises(sqlalchemy.exc.OperationalError):
            p = Place(**self.para)
            p.save()

    def test_place_description_edge(self):
        """Test operation of saving a Place object with `description` at edge
        of column constraint"""
        self.para['description'] = 'f' * 1024
        p = Place(**self.para)
        p.save()
        id = p.id
        self.cur.execute("SELECT id FROM places WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])

    def test_place_description_invalid(self):
        """Test operation of saving a Place object with `description` over
        column constraint"""
        self.para['description'] = 'c' * 1025
        with self.assertRaises(sqlalchemy.exc.DataError):
            p = Place(**self.para)
            p.save()

    def test_place_description_none(self):
        """Test operation of saving a Place object with no `description`"""
        del self.para['description']
        p = Place(**self.para)
        p.save()
        id = p.id
        self.cur.execute("SELECT id FROM places WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])

    def test_place_number_rooms_none(self):
        """Test operation of saving a Place object with no `number_rooms`"""
        del self.para['number_rooms']
        p = Place(**self.para)
        p.save()
        id = p.id
        self.cur.execute("SELECT id FROM places WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])

    def test_place_number_bathrooms_none(self):
        """Test operation of saving a Place object with no `number_bathrooms`
        """
        del self.para['number_bathrooms']
        p = Place(**self.para)
        p.save()
        id = p.id
        self.cur.execute("SELECT id FROM places WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])

    def test_place_max_guest_none(self):
        """Test operation of saving a Place object with no `max_guest`"""
        del self.para['max_guest']
        p = Place(**self.para)
        p.save()
        id = p.id
        self.cur.execute("SELECT id FROM places WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])

    def test_place_price_by_night_none(self):
        """Test operation of saving a Place object with no `price_by_night`"""
        del self.para['price_by_night']
        p = Place(**self.para)
        p.save()
        id = p.id
        self.cur.execute("SELECT id FROM places WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])

    def test_place_latitude_none(self):
        """Test operation of saving a Place object with no `latitude`"""
        del self.para['latitude']
        p = Place(**self.para)
        p.save()
        id = p.id
        self.cur.execute("SELECT id FROM places WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])

    def test_place_longitude_none(self):
        """Test operation of saving a Place object with no `longitude`"""
        del self.para['longitude']
        p = Place(**self.para)
        p.save()
        id = p.id
        self.cur.execute("SELECT id FROM places WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])

    def test_place_deletion(self):
        """Test operation of saving a Place object with valid attributes"""
        p = Place(**self.para)
        p.save()
        id = p.id
        r = Review(place_id=id, user_id=self.uid, text="amazing")
        r.save()
        self.cur.execute("SELECT places.id, reviews.id FROM places, reviews\
        WHERE places.id = reviews.place_id AND reviews.id = '{}'".format(r.id))
        rows = self.cur.fetchall()
        self.assertEqual(id, rows[0][0])
        self.assertEqual(r.id, rows[0][1])

        storage.delete(p)
        storage.save()
        self.tearDown()
        self.create_conn()

        self.cur.execute("SELECT id FROM places WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertEqual((), rows)

        self.cur.execute("SELECT id FROM reviews WHERE id = '{}'".format(r.id))
        rows = self.cur.fetchall()
        self.assertEqual((), rows)

if __name__ == "__main__":
    unittest.main()
