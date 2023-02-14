#!/usr/bin/python3
"""This is the place class"""
from models.base_model import BaseModel, Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
import os


association_table = Table("place_amenity", Base.metadata,
                          Column("place_id", String(60),
                                 ForeignKey("places.id"), primary_key=True,
                                 nullable=False),
                          Column("amenity_id", String(60),
                                 ForeignKey("amenities.id"), primary_key=True,
                                 nullable=False))


class Place(BaseModel, Base):
    """This is the class for Place
    Attributes:
        city_id: city id
        user_id: user id
        name: name input
        description: string of description
        number_rooms: number of room in int
        number_bathrooms: number of bathrooms in int
        max_guest: maximum guest in int
        price_by_night: price for a staying in int
        latitude: latitude in flaot
        longitude: longitude in float
        amenity_ids: list of Amenity ids
    """
    __tablename__ = 'places'
    city_id = Column(String(60), ForeignKey('cities.id'), nullable=False)
    user_id = Column(String(60), ForeignKey('users.id'), nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(String(1024))
    number_rooms = Column(Integer, default=0, nullable=False)
    number_bathrooms = Column(Integer, default=0, nullable=False)
    max_guest = Column(Integer, default=0, nullable=False)
    price_by_night = Column(Integer, default=0, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    amenity_ids = []

    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        reviews = relationship('Review', backref='place',
                               cascade='all, delete')
    amenities = relationship("Amenity", secondary="place_amenity",
                             viewonly=False)

    if os.getenv("HBNB_TYPE_STORAGE") != "db":
        @property
        def reviews(self):
            '''Gets all Reviews instances where place_id == current Place.id'''
            new_list = []
            for each in storage.all('Review').items():
                if self.id == each.place_id:
                    new_list.append(each)
            return new_list

        @property
        def amenities(self):
            '''Gets all Amenity instances where amenity_ids==self.id'''
            new_list = []
            for each in models.storage.all(Amenity).values():
                if each.id in self.amenity_ids:
                    new_list.append(each)
            return new_list

        @amenities.setter
        def amenities(self, obj):
            '''Setter for amenities'''
            if isinstance(obj, Amenity):
                self.amenity_ids.append(obj.id)
