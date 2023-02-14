#!/usr/bin/python3
"""test for review"""
import unittest
import os
from models.review import Review
from models.user import User
from models.state import State
from models.city import City
from models.place import Place
from models.base_model import BaseModel
import pep8
from models import storage
import sqlalchemy
import MySQLdb


class TestReview(unittest.TestCase):
    """this will test the place class"""

    @classmethod
    def setUpClass(cls):
        """set up for test"""
        if os.getenv('HBNB_TYPE_STORAGE') == 'db':
            return
        cls.rev = Review()
        cls.rev.place_id = "4321-dcba"
        cls.rev.user_id = "123-bca"
        cls.rev.text = "The srongest in the Galaxy"

    @classmethod
    def teardown(cls):
        """at the end of the test this will tear it down"""
        del cls.rev

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
        p = style.check_files(['models/review.py'])
        self.assertEqual(p.total_errors, 0, "fix pep8")

    def test_checking_for_docstring_Review(self):
        """checking for docstrings"""
        self.assertIsNotNone(Review.__doc__)

    def test_attributes_review(self):
        """chekcing if review have attributes"""
        self.assertTrue('id' in self.rev.__dict__)
        self.assertTrue('created_at' in self.rev.__dict__)
        self.assertTrue('updated_at' in self.rev.__dict__)
        self.assertTrue('place_id' in self.rev.__dict__)
        self.assertTrue('text' in self.rev.__dict__)
        self.assertTrue('user_id' in self.rev.__dict__)

    def test_is_subclass_Review(self):
        """test if review is subclass of BaseModel"""
        self.assertTrue(issubclass(self.rev.__class__, BaseModel), True)

    def test_attribute_types_Review(self):
        """test attribute type for Review"""
        self.assertEqual(type(self.rev.text), str)
        self.assertEqual(type(self.rev.place_id), str)
        self.assertEqual(type(self.rev.user_id), str)

    def test_save_Review(self):
        """test if the save works"""
        self.rev.save()
        self.assertNotEqual(self.rev.created_at, self.rev.updated_at)

    def test_to_dict_Review(self):
        """test if dictionary works"""
        self.assertEqual('to_dict' in dir(self.rev), True)


class TestReviewDb(unittest.TestCase):
    """This will test the Review class on DB storage"""

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

        cls.para = {'city_id': cls.cid, 'user_id': cls.uid,
                    'name': 'Home', 'description': 'Something',
                    'number_rooms': 10, 'number_bathrooms': 11,
                    'max_guest': 12, 'price_by_night': 9000,
                    'latitude': 0.0, 'longitude': 1.1}
        p = Place(**cls.para)
        p.save()
        cls.pid = p.id

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

    def test_review_normal(self):
        """Test operation of saving a Review object with valid attributes"""
        r = Review(place_id=self.pid, user_id=self.uid, text="Great")
        r.save()
        id = r.id
        self.cur.execute("SELECT id FROM reviews WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])

    def test_review_text_edge(self):
        """Test operation of saving a Review object with `text` at edge of
        column constraint"""
        r = Review(place_id=self.pid, user_id=self.uid, text="G" * 1024)
        r.save()
        id = r.id
        self.cur.execute("SELECT id FROM reviews WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])

    def test_review_text_invalid(self):
        """Test operation of saving a Review object with `text` over column
        constraint"""
        with self.assertRaises(sqlalchemy.exc.DataError):
            r = Review(place_id=self.pid, user_id=self.uid, text="G" * 1025)
            r.save()

    def test_review_text_none(self):
        """Test operation of saving a Review object with no `text`"""
        with self.assertRaises(sqlalchemy.exc.OperationalError):
            r = Review(place_id=self.pid, user_id=self.uid)
            r.save()

    def test_review_deletion(self):
        """Test deletion of a Review object"""
        r = Review(place_id=self.pid, user_id=self.uid, text="Great")
        r.save()
        id = r.id
        self.cur.execute("SELECT id FROM reviews WHERE id = '{}'".format(id))
        rows = self.cur.fetchall()
        self.assertIn(id, rows[0])

        storage.delete(r)
        storage.save()
        self.tearDown()
        self.create_conn()

        self.cur.execute("SELECT COUNT(id) FROM reviews WHERE id = '{}'"
                         .format(id))
        count = self.cur.fetchall()[0][0]
        self.assertEqual(0, count)

    def test_Review_place_id_invalid(self):
        """Test operation of saving a Review object with invalid `place_id`"""
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            r = Review(place_id='fdfsfsdf', user_id=self.uid, text="nope")
            r.save()

    def test_Review_place_id_none(self):
        """Test operation of saving a Review object with no `place_id`"""
        with self.assertRaises(sqlalchemy.exc.OperationalError):
            r = Review(user_id=self.uid, text="Nope")
            r.save()

    def test_Review_user_id_invalid(self):
        """Test operation of saving a Review object with invalid `user_id`"""
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            r = Review(user_id='fdfsfsdf', place_id=self.pid, text="nope")
            r.save()

    def test_Review_user_id_none(self):
        """Test operation of saving a Review object with no `user_id`"""
        with self.assertRaises(sqlalchemy.exc.OperationalError):
            r = Review(place_id=self.pid, text="Nope")
            r.save()


if __name__ == "__main__":
    unittest.main()
