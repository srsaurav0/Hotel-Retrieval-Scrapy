# Hotel Retrieval Scrapy

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup and Installation](#setup-and-installation)
- [Project Structure](#project-structure)
- [Accessing the Database](#accessing-the-database)
- [Database Schema](#database-schema)
- [Image Storage](#image-storage)
- [Testing](#testing)



---


## Introduction

This project scrapes hotel data from the [Trip.com](https://uk.trip.com/hotels/?locale=en-GB&curr=GBP) website, stores the data in a PostgreSQL database, and saves hotel images in organized directories.


---


## Features

- Scrapes city and hotel data, including city names, hotel names, prices, ratings, locations, and room types.
- Stores data in a PostgreSQL database using SQLAlchemy.
- Saves hotel images to directories organized by city names.
- Provides automated tests for spiders, models, and functionalities.


---


## Prerequisites

- Docker and Docker Compose installed
- Python 3.9+


---


## Setup and Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/srsaurav0/Hotel-Retrieval-Scrapy.git
   cd Hotel-Retrieval-Scrapy
   ```

2. Create and activate a virtual environment:
   On Linux:
   ```bash
    python3 -m venv .venv
    source .venv/bin/activate
   ```
   On Windows:
   ```bash
    python -m venv .venv
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    .venv\Scripts\activate
   ```

3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
   
   Executing this command will: 
   -    Initialize the database.
   -    Fetch data from **3 cities** of **at most 10 hotels** belonging to that city. 
   -    This data will be stored on database. 
   -    Additionally, the scraped data can also be viewed from the console log. 
   -    The images of the hotels will be stored in the ***images*** folder. It will be stored under the **city name** so that it is convenient to retrieve and view.


---


## Project Structure

```bash
├── hotel_scraper
│   ├── spiders
│   │   ├── city_hotels.py       # Scrapy spider to scrape data
│   ├── database.py              # SQLAlchemy database setup
│   ├── check_tables.py          # SQLAlchemy models for City and Hotel
│   ├── items.py                 # Items for City and Hotel
│   ├── middlewares.py           # Middlewares
│   ├── models.py                # SQLAlchemy models for City and Hotel
│   ├── pipelines.py             # Pipelines
│   ├── settings.py              # Settings
├── tests
│   ├── test_spider.py           # Unit tests for the scraper
│   ├── test_database.py         # Unit tests for database models
│   ├── test_middleware.py       # Unit tests for middleware
├── Dockerfile                   # Dockerfile for scraper
├── docker-compose.yml           # Docker Compose configuration
├── initialize_db.py             # File to initialize database
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
```


---


## Accessing the Database

1. Access the PostgreSQL container:
   ```bash
   docker exec -it postgres_db bash
   ```

2. Use `psql` to connect to the database:
   ```bash
   psql -U user hotels_db
   ```

3. Run SQL queries to inspect data:
   ```sql
   SELECT * FROM cities;
   SELECT * FROM hotels;
   ```


---


## Database Schema

### City Table
| Column  | Type   | Description       |
|---------|--------|-------------------|
| id      | Integer| Primary Key       |
| name    | String | City Name         |

### Hotel Table
| Column       | Type    | Description                    |
|--------------|---------|--------------------------------|
| id           | Integer | Primary Key                   |
| name         | String  | Hotel Name                    |
| rating       | Float   | Hotel Rating                  |
| location     | String  | Hotel Location                |
| latitude     | Float   | Hotel Latitude                |
| longitude    | Float   | Hotel Longitude               |
| room_type    | String  | Hotel Room Type               |
| price        | Float   | Hotel Price                   |
| image_path   | String  | Path to Saved Image           |
| city_id      | Integer | Foreign Key (City Table)      |


---


## Image Storage

- All hotel images are stored in the `images/` directory, organized by city names.
- The path to each image is saved in the database for easy retrieval.


---


## Testing

1. Enter into scraper container:
   ```bash
   docker exec -it scraper bash
   ```

2. Run all tests:
   ```bash
   pytest
   ```

3. Run all tests with coverage:
   ```bash
   pytest --cov=hotel_scraper
   ```

