#!/usr/bin/python3
"""test for state"""
import unittest
import os
from models.state import State
from models.city import City
from models.base_model import BaseModel
import pep8
import sqlalchemy
import MySQLdb
from models import storage


class TestState(unittest.TestCase):
    """this will test the State class"""

    @classmethod
    def setUpClass(cls):
        """set up for test"""
        if os.getenv('HBNB_TYPE_STORAGE') == 'db':
            return
        cls.state = State()
        cls.state.name = "CA"

    @classmethod
    def teardown(cls):
        """at the end of the test this will tear it down"""
        del cls.state

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

    def test_pep8_Review(self):
        """Tests pep8 style"""
        style = pep8.StyleGuide(quiet=True)
        p = style.check_files(['models/state.py'])
        self.assertEqual(p.total_errors, 0, "fix pep8")

    def test_checking_for_docstring_State(self):
        """checking for docstrings"""
        self.assertIsNotNone(State.__doc__)

    def test_attributes_State(self):
        """chekcing if State have attributes"""
        self.assertTrue('id' in self.state.__dict__)
        self.assertTrue('created_at' in self.state.__dict__)
        self.assertTrue('updated_at' in self.state.__dict__)
        self.assertTrue('name' in self.state.__dict__)

    def test_is_subclass_State(self):
        """test if State is subclass of BaseModel"""
        self.assertTrue(issubclass(self.state.__class__, BaseModel), True)

    def test_attribute_types_State(self):
        """test attribute type for State"""
        self.assertEqual(type(self.state.name), str)

    def test_save_State(self):
        """test if the save works"""
        self.state.save()
        self.assertNotEqual(self.state.created_at, self.state.updated_at)

    def test_to_dict_State(self):
        """test if dictionary works"""
        self.assertEqual('to_dict' in dir(self.state), True)


class TestStateDb(unittest.TestCase):
    """This will test the State class on DB storage"""

    def setUp(self):
        """Setup method"""
        if os.getenv('HBNB_TYPE_STORAGE') != 'db':
            self.skipTest("Using file storage")
        storage.reload()
        self.conn = MySQLdb.connect(host=os.getenv('HBNB_MYSQL_HOST'),
                                    port=3306,
                                    user=os.getenv('HBNB_MYSQL_USER'),
                                    passwd=os.getenv('HBNB_MYSQL_PWD'),
                                    db=os.getenv('HBNB_MYSQL_DB'),
                                    charset="utf8")

        self.cur = self.conn.cursor()

    def tearDown(self):
        """Teardown method to reload session"""
        self.cur.close()
        self.conn.close()

    def test_state_normal(self):
        """Test operation of saving a state object with valid attributes"""
        s = State()
        s.name = "California"
        s.save()
        id = s.id
        self.cur.execute("SELECT id FROM states WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])

    def test_state_edge(self):
        """Test operation of saving a State object with an attribute at the max
        of column constraint to db"""
        s = State()
        s.name = 'A' * 128
        s.save()
        id = s.id
        self.cur.execute("SELECT id FROM states WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])

    def test_state_error(self):
        """Test operation of saving a State object with an attribute that
        violates column constraints to db"""
        with self.assertRaises(sqlalchemy.exc.DataError):
            s = State()
            s.name = 'T' * 129
            s.save()

    def test_state_deletion(self):
        """Test operation of saving a state object with valid attributes"""
        s = State(name="California")
        s.save()
        id = s.id
        c = City(name="San Francisco!!!!", state_id=id)
        c.save()
        cid = c.id
        if cid is None:
            self.skipTest("Failed to save City object to db")
        self.cur.execute("SELECT states.id, cities.id FROM states, cities\
        WHERE states.id = cities.state_id AND states.id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])
        self.assertIn(cid, rows[0])

        storage.delete(s)
        storage.save()
        self.tearDown()
        self.setUp()
        self.cur.execute("SELECT id FROM states WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertEqual((), rows)
        self.cur.execute("SELECT id FROM cities WHERE id = '{}'".format(cid))
        rows = self.cur.fetchall()
        self.assertEqual((), rows)


if __name__ == "__main__":
    unittest.main()
