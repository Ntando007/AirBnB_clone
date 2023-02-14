#!/usr/bin/python3
"""test for city"""
import unittest
import os
from models.city import City
from models.state import State
from models.user import User
from models.place import Place
from models.base_model import BaseModel
import pep8
import sqlalchemy
import MySQLdb
from models import storage


class TestCity(unittest.TestCase):
    """this will test the city class"""

    @classmethod
    def setUpClass(cls):
        """set up for test"""
        if os.getenv('HBNB_TYPE_STORAGE') == 'db':
            return
        cls.city = City()
        cls.city.name = "LA"
        cls.city.state_id = "CA"

    @classmethod
    def teardown(cls):
        """at the end of the test this will tear it down"""
        del cls.city

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

    def test_pep8_City(self):
        """Tests pep8 style"""
        style = pep8.StyleGuide(quiet=True)
        p = style.check_files(['models/city.py'])
        self.assertEqual(p.total_errors, 0, "fix pep8")

    def test_checking_for_docstring_City(self):
        """checking for docstrings"""
        self.assertIsNotNone(City.__doc__)

    def test_attributes_City(self):
        """chekcing if City have attributes"""
        self.assertTrue('id' in self.city.__dict__)
        self.assertTrue('created_at' in self.city.__dict__)
        self.assertTrue('updated_at' in self.city.__dict__)
        self.assertTrue('state_id' in self.city.__dict__)
        self.assertTrue('name' in self.city.__dict__)

    def test_is_subclass_City(self):
        """test if City is subclass of Basemodel"""
        self.assertTrue(issubclass(self.city.__class__, BaseModel), True)

    def test_attribute_types_City(self):
        """test attribute type for City"""
        self.assertEqual(type(self.city.name), str)
        self.assertEqual(type(self.city.state_id), str)

    def test_save_City(self):
        """test if the save works"""
        self.city.save()
        self.assertNotEqual(self.city.created_at, self.city.updated_at)

    def test_to_dict_City(self):
        """test if dictionary works"""
        self.assertEqual('to_dict' in dir(self.city), True)


class TestCityDb(unittest.TestCase):
    """This will test the City class on DB storage"""

    @classmethod
    def setUpClass(cls):
        """Create and save a State object to be used during testing of City"""
        cls.s = State()
        cls.s.name = "California"
        cls.s.save()
        cls.sid = cls.s.id

    @classmethod
    def tearDownClass(cls):
        """Delete State object"""
        del cls.s

    def setUp(self):
        """Setup method"""
        if os.getenv('HBNB_TYPE_STORAGE') != 'db':
            self.skipTest("Using file storage")
        if self.sid is None:
            self.skipTest("Failed to save a State object into db")
        self.create_conn()

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

    def test_city_normal(self):
        """Test operation of saving a city object with valid attributes"""
        c = City()
        c.name = "San Francisco"
        c.state_id = self.sid
        c.save()
        id = c.id
        self.cur.execute("SELECT cities.id, states.id FROM cities, states\
        WHERE states.id = cities.state_id AND cities.id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])
        self.assertIn(self.sid, rows[0])

    def test_city_name_edge(self):
        """Test operation of saving a City object with the attribute `name` at
        max column constraint to db"""
        c = City()
        c.name = 'A' * 128
        c.state_id = self.sid
        c.save()
        id = c.id
        self.cur.execute("SELECT id FROM cities WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])

    def test_city_name_error(self):
        """Test operation of saving a City object with the attribute `name`
        violating column constraint to db"""
        with self.assertRaises(sqlalchemy.exc.DataError):
            c = City()
            c.name = 'T' * 129
            c.state_id = self.sid
            c.save()

    def test_city_state_error(self):
        """Test operation of saving a City object the attribute `state_id` as
        None"""
        with self.assertRaises(sqlalchemy.exc.OperationalError):
            c = City()
            c.name = "Nooooo"
            c.save()

    def test_city_delete(self):
        """Test operation of deleting a City object"""
        c = City(name="San Francisco", state_id=self.sid)
        c.save()
        id = c.id
        u = User(email='Betty@holberton.com', password='Hello')
        u.save()
        p = Place(city_id=id, user_id=u.id, name='Home', number_rooms=10,
                  number_bathrooms=10, max_guest=10, price_by_night=9000)
        p.save()
        self.cur.execute("SELECT cities.id, states.id FROM cities, states\
        WHERE states.id = cities.state_id AND cities.id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])
        self.assertIn(self.sid, rows[0])

        self.cur.execute("SELECT cities.id, places.id FROM cities, places\
        WHERE places.city_id = cities.id AND cities.id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(p.id, rows[0])

        storage.delete(c)
        storage.save()

        self.tearDown()
        self.create_conn()
        self.cur.execute("SELECT COUNT(id) FROM cities WHERE id = '{}'"
                         .format(id))
        count = self.cur.fetchall()[0][0]
        self.assertEqual(0, count)

        self.cur.execute("SELECT COUNT(id) FROM places WHERE id = '{}'"
                         .format(p.id))
        count = self.cur.fetchall()[0][0]
        self.assertEqual(0, count)


if __name__ == "__main__":
    unittest.main()
