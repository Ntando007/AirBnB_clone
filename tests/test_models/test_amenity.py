#!/usr/bin/python3
"""test for amenity"""
import unittest
import os
from models.amenity import Amenity
from models.base_model import BaseModel
import pep8
import MySQLdb
import sqlalchemy
from models import storage


class TestAmenity(unittest.TestCase):
    """this will test the Amenity class"""

    @classmethod
    def setUpClass(cls):
        """set up for test"""
        if os.getenv('HBNB_TYPE_STORAGE') == 'db':
            return
        cls.amenity = Amenity()
        cls.amenity.name = "Breakfast"

    @classmethod
    def teardown(cls):
        """at the end of the test this will tear it down"""
        del cls.amenity

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

    def test_pep8_Amenity(self):
        """Tests pep8 style"""
        style = pep8.StyleGuide(quiet=True)
        p = style.check_files(['models/amenity.py'])
        self.assertEqual(p.total_errors, 0, "fix pep8")

    def test_checking_for_docstring_Amenity(self):
        """checking for docstrings"""
        self.assertIsNotNone(Amenity.__doc__)

    def test_attributes_Amenity(self):
        """chekcing if amenity have attibutes"""
        self.assertTrue('id' in self.amenity.__dict__)
        self.assertTrue('created_at' in self.amenity.__dict__)
        self.assertTrue('updated_at' in self.amenity.__dict__)
        self.assertTrue('name' in self.amenity.__dict__)

    def test_is_subclass_Amenity(self):
        """test if Amenity is subclass of Basemodel"""
        self.assertTrue(issubclass(self.amenity.__class__, BaseModel), True)

    def test_attribute_types_Amenity(self):
        """test attribute type for Amenity"""
        self.assertEqual(type(self.amenity.name), str)

    def test_save_Amenity(self):
        """test if the save works"""
        self.amenity.save()
        self.assertNotEqual(self.amenity.created_at, self.amenity.updated_at)

    def test_to_dict_Amenity(self):
        """test if dictionary works"""
        self.assertEqual('to_dict' in dir(self.amenity), True)


class TestAmenityDb(unittest.TestCase):
    """This will test the Amenity class on DB storage"""

    @classmethod
    def setUpClass(cls):
        """Setup for the test"""
        if os.getenv('HBNB_TYPE_STORAGE') != 'db':
            return

    def setUp(self):
        """Setup method"""
        if os.getenv('HBNB_TYPE_STORAGE') != 'db':
            self.skipTest("Using file storage")
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

    def test_amenity_normal(self):
        """Test normal save operation of Amenity object"""
        a = Amenity(name="TV")
        a.save()
        id = a.id
        self.cur.execute("SELECT id FROM amenities WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertEqual(id, rows[0][0])

    def test_amenity_name_edge(self):
        """Test operation of saving a Amenity object with `name` at edge of
        column constraint"""
        a = Amenity(name="T" * 128)
        a.save()
        id = a.id
        self.cur.execute("SELECT id FROM amenities WHERE id = '{}'"
                         .format(a.id))
        rows = self.cur.fetchall()
        self.assertEqual(id, rows[0][0])

    def test_amenity_name_invalid(self):
        """Test operation of saving a Amenity object with `name` over column
        constraint"""
        with self.assertRaises(sqlalchemy.exc.DataError):
            a = Amenity(name="T" * 129)
            a.save()

    def test_amenity_name_none(self):
        """Test operation of saving a Amenity object with no `name`"""
        with self.assertRaises(sqlalchemy.exc.OperationalError):
            a = Amenity()
            a.save()

    def test_amenity_deletion(self):
        """Test deletion operation of an Amenity object"""
        a = Amenity(name="TV")
        a.save()
        id = a.id
        self.cur.execute("SELECT id FROM amenities WHERE id = '{}'"
                         .format(id))
        rows = self.cur.fetchall()
        self.assertEqual(id, rows[0][0])

        storage.delete(a)
        storage.save()
        self.tearDown()
        self.create_conn()
        self.cur.execute("SELECT id FROM amenities WHERE id = '{}'"
                         .format(id))
        rows = self.cur.fetchall()
        self.assertEqual((), rows)

if __name__ == "__main__":
    unittest.main()
