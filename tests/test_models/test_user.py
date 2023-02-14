#!/usr/bin/python3
"""test for user"""
import unittest
import os
from models.user import User
from models.state import State
from models.place import Place
from models.city import City
from models.review import Review
from models.base_model import BaseModel
import pep8
import MySQLdb
from models import storage
import sqlalchemy


class TestUser(unittest.TestCase):
    """this will test the User class"""

    @classmethod
    def setUpClass(cls):
        """set up for test"""
        if os.getenv('HBNB_TYPE_STORAGE') == 'db':
            return
        cls.user = User()
        cls.user.first_name = "Kevin"
        cls.user.last_name = "Yook"
        cls.user.email = "yook00627@gmamil.com"
        cls.user.password = "secret"

    @classmethod
    def teardown(cls):
        """at the end of the test this will tear it down"""
        del cls.user

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

    def test_pep8_User(self):
        """Tests pep8 style"""
        style = pep8.StyleGuide(quiet=True)
        p = style.check_files(['models/user.py'])
        self.assertEqual(p.total_errors, 0, "fix pep8")

    def test_checking_for_docstring_User(self):
        """checking for docstrings"""
        self.assertIsNotNone(User.__doc__)

    def test_attributes_User(self):
        """chekcing if User have attributes"""
        self.assertTrue('email' in self.user.__dict__)
        self.assertTrue('id' in self.user.__dict__)
        self.assertTrue('created_at' in self.user.__dict__)
        self.assertTrue('updated_at' in self.user.__dict__)
        self.assertTrue('password' in self.user.__dict__)
        self.assertTrue('first_name' in self.user.__dict__)
        self.assertTrue('last_name' in self.user.__dict__)

    def test_is_subclass_User(self):
        """test if User is subclass of Basemodel"""
        self.assertTrue(issubclass(self.user.__class__, BaseModel), True)

    def test_attribute_types_User(self):
        """test attribute type for User"""
        self.assertEqual(type(self.user.email), str)
        self.assertEqual(type(self.user.password), str)
        self.assertEqual(type(self.user.first_name), str)
        self.assertEqual(type(self.user.first_name), str)

    def test_save_User(self):
        """test if the save works"""
        self.user.save()
        self.assertNotEqual(self.user.created_at, self.user.updated_at)

    def test_to_dict_User(self):
        """test if dictionary works"""
        self.assertEqual('to_dict' in dir(self.user), True)


class TestUserDb(unittest.TestCase):
    """This will test the City class on DB storage"""

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
        """Create mysqldb connection"""
        self.conn = MySQLdb.connect(host=os.getenv('HBNB_MYSQL_HOST'),
                                    port=3306,
                                    user=os.getenv('HBNB_MYSQL_USER'),
                                    passwd=os.getenv('HBNB_MYSQL_PWD'),
                                    db=os.getenv('HBNB_MYSQL_DB'),
                                    charset="utf8")

        self.cur = self.conn.cursor()

    def test_user_normal(self):
        """Test operation of saving a User object with valid attributes"""
        u = User(email="Betty@Holberton.com", password="Hello",
                 first_name="Betty", last_name="Holberton")
        u.save()
        id = u.id
        self.cur.execute("SELECT id FROM users WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])

    def test_user_email_edge(self):
        """Test operation of saving a User object with the attribute `email` at
        max column constraint to db"""
        u = User(email='A' * 128, password="Hello",
                 first_name="Betty", last_name="Holberton")
        u.save()
        id = u.id
        self.cur.execute("SELECT id FROM users WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])

    def test_user_email_error(self):
        """Test operation of saving a User object with the attribute `email`
        violating column constraint to db"""
        with self.assertRaises(sqlalchemy.exc.DataError):
            u = User(email='O' * 129, password="Hello",
                     first_name="Betty", last_name="Holberton")
            u.save()

    def test_user_password_edge(self):
        """Test operation of saving a User object with the attribute `password`
        at max column constraint to db"""
        u = User(email="Betty@Holberton.com", password='P' * 128,
                 first_name="Betty", last_name="Holberton")
        u.save()
        id = u.id
        self.cur.execute("SELECT id FROM users WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])

    def test_user_password_error(self):
        """Test operation of saving a User object with the attribute `password`
        violating column constraint to db"""
        with self.assertRaises(sqlalchemy.exc.DataError):
            u = User(email="Betty@Holberton.com", password='A' * 129,
                     first_name="Betty", last_name="Holberton")
            u.save()

    def test_user_first_edge(self):
        """Test operation of saving a User object with the attribute
        `first_name` at max column constraint to db"""
        u = User(email="Betty@Holberton.com", password="Hello",
                 first_name='B' * 128, last_name="Holberton")
        u.save()
        id = u.id
        self.cur.execute("SELECT id FROM users WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])

    def test_user_first_error(self):
        """Test operation of saving a User object with the attribute
        `first_name` violating column constraint to db"""
        with self.assertRaises(sqlalchemy.exc.DataError):
            u = User(email="Betty@Holberton.com", password="Hello",
                     first_name='K' * 129, last_name="Holberton")
            u.save()

    def test_user_last_edge(self):
        """Test operation of saving a User object with the attribute
        `last_name` at max column constraint to db"""
        u = User(email="Betty@Holberton.com", password="Hello",
                 first_name="Betty", last_name='H' * 128)
        u.save()
        id = u.id
        self.cur.execute("SELECT id FROM users WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])

    def test_user_last_error(self):
        """Test operation of saving a User object with the attribute
        `last_name` violating column constraint to db"""
        with self.assertRaises(sqlalchemy.exc.DataError):
            u = User(email="Betty@Holberton.com", password="Hello",
                     first_name="Betty", last_name='H' * 129)
            u.save()

    def test_allowed_null(self):
        """Test operation of saving a User object with allowed NULLS"""
        u = User(email="Betty@Holberton.com", password="NoNames")
        u.save()
        id = u.id
        self.cur.execute("SELECT id FROM users WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])

    def test_no_null_0(self):
        """Test operation of saving a User object with not allowed NULLS"""
        with self.assertRaises(sqlalchemy.exc.OperationalError):
            u = User(email="Betty@Holberton.com")
            u.save()

    def test_no_null_1(self):
        """Test operationo f saving a User object with not allowed NULLS"""
        with self.assertRaises(sqlalchemy.exc.OperationalError):
            u = User(password="NoEmail")
            u.save()

    def test_user_delete(self):
        """Test operation of deleting a City object"""
        u = User(email="Betty@Holberton.com", password="Hello",
                 first_name="Betty", last_name="Holberton")
        u.save()
        id = u.id
        s = State(name="NY")
        s.save()
        c = City(name='NYC', state_id=s.id)
        c.save()
        p = Place(city_id=c.id, user_id=id, name="Home", number_rooms=10,
                  number_bathrooms=10, max_guest=10, price_by_night=9000)
        p.save()
        r = Review(place_id=p.id, user_id=id, text="Greeat")
        r.save()
        self.cur.execute("SELECT id FROM users WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertEqual(id, rows[0][0])

        self.cur.execute("SELECT users.id, places.id FROM users, places\
        WHERE users.id = places.user_id AND users.id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertEqual(p.id, rows[0][1])

        self.cur.execute("SELECT users.id, reviews.id FROM users, reviews\
        WHERE users.id = reviews.user_id AND users.id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertEqual(r.id, rows[0][1])

        storage.delete(u)
        storage.save()
        self.tearDown()
        self.create_conn()
        self.cur.execute("SELECT COUNT(id) FROM users WHERE id = '{}'"
                         .format(id))
        count = self.cur.fetchall()[0][0]
        self.assertEqual(0, count)

        self.cur.execute("SELECT COUNT(id) FROM places WHERE id = '{}'"
                         .format(p.id))
        count = self.cur.fetchall()[0][0]
        self.assertEqual(0, count)

        self.cur.execute("SELECT COUNT(id) FROM reviews WHERE id = '{}'"
                         .format(r.id))
        count = self.cur.fetchall()[0][0]
        self.assertEqual(0, count)


if __name__ == "__main__":
    unittest.main()
