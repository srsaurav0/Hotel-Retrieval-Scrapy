from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from hotel_scraper.database import Base

class City(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    hotels = relationship("Hotel", back_populates="city")

class Hotel(Base):
    __tablename__ = 'hotels'

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer)
    name = Column(String, index=True)
    rating = Column(Float)
    location = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    room_type = Column(String)
    price = Column(Float)
    image_path = Column(String)  # Path to the saved image
    city_id = Column(Integer, ForeignKey('cities.id'))
    city_name = Column(String)
    city = relationship("City", back_populates="hotels")
