from app import db
import pickle
import json
import sklearn
import datetime
tables = {"car", "carAvailability", "carTripHistory", "faqs", "rating", "user"}

def test():
    return read_from_table("car", 5)

# def _search(table, field, keyword, amount=5):
#     assert table in tables
#     with db.begin() as conn:
#         res = conn.execute(f"SELECT * FROM {table} WHERE {field} LIKE '%{keyword}%").fetchmany(amount)
#     return res

def get_your_trip_history(user_id, amount=10):
    query = f"""
    SELECT 
        journey_id, car_id, pickup_datetime, dropoff_datetime,
        price, rating 
    FROM carTripHistory
    WHERE lesser_id='{user_id}';
    """
    with db.begin() as conn:
        res = conn.execute(query)
    return [r for r in res]

def read_from_table(table, amount=5):
    assert table in tables
    with db.begin() as conn:
        res = conn.execute(f"SELECT * FROM {table} LIMIT {amount}").fetchall()
    return [r for r in res]


def fetch_car(pic_lat, pic_lon, pic_dt, drop_dt,is_make, is_year, make, year):
    conn = db.connect()

    q = f"""
    SELECT 
        car.car_id, car_lat, car_lon, make, model, year, VIN, availability_id, availability_from, availability_till,
        ROUND(POWER(POWER(car_lat-'{pic_lat}',2) + POWER(car_lon-'{pic_lon}',2), 0.5),5) AS distance
    FROM carAvailability 
    JOIN car ON car.car_id = carAvailability.car_id
    WHERE availability_from >= '{pic_dt}' AND availability_till <= '{drop_dt}'
    """
    if is_make:
        s = f" AND make = '{make}'"
        q = q + s
    if is_year:
        s = f" AND year = '{year}'"
        q = q + s
    q = q + " ORDER BY distance ASC;"
    car_details = conn.execute(q)
    car_details = [r for r in car_details]  
    with open('model.sav' , 'rb') as f:
        model = pickle.load(f)
    with open("car_model_categ.json", "r") as f:
        car_categories = json.load(f)
    car_categories = car_categories[0]
    
    pic_dt  = datetime.datetime.strptime(pic_dt, "%Y-%m-%d %H:%M")
    drop_dt = datetime.datetime.strptime(drop_dt, "%Y-%m-%d %H:%M")

    all_prices = []
    for i in range(len(car_details)):
        lat = car_details[i][1]
        lon = car_details[i][2]
        cm = car_details[i][4]
        try:
            mo = car_categories[carmodel]
        except:
            mo = 0
        yr = car_details[i][5]
        dur = (drop_dt - pic_dt).total_seconds()/60
        if dur > 600: dur = 600
        price = model.predict([[lat, lon, mo, yr, dur]])[0]
        # Michael's changes - convert cents to dollars
        price = price / 100
        all_prices.append(price)
    conn.close()
    return car_details, all_prices

def advanced_query_top_rated_cars():
    # Query 1: (Car location details with > 4.0 rating and > 50 trips)
    conn = db.connect()
    q = """
    SELECT 
		car.car_id, 
	    car_lat, 
	    car_lon,
	    AVG(rating) AS avg_rating,
	    COUNT(*) AS total_trips
	FROM car
	JOIN carTripHistory ON car.car_id = carTripHistory.car_id
	GROUP BY car.car_id
	HAVING avg_rating >=4 AND total_trips >=50
	ORDER BY total_trips DESC, avg_rating DESC;
    """
    res = conn.execute(q)
    return [r for r in res]

def advanced_query_new_cars_without_trips():
    # Query 2: (Show car availability of cars without any trip history
    conn = db.connect()
    q = """
    SELECT 
		car.car_id, 
        make, 
        model, 
        year, 
        availability_from, availability_till
	FROM carAvailability 
	JOIN car ON car.car_id = carAvailability.car_id
	WHERE availability_from >= CURDATE() AND availability_till <=ADDDATE(CURDATE(), 5)
	AND car.car_id NOT IN (SELECT DISTINCT car_id FROM carTripHistory)
    ORDER BY availability_from DESC;
    """
    
    res = conn.execute(q)
    return [r for r in res]

def add_car(carID, carLat, carLong, make, model, year, VIN, owner_id):
    with db.begin() as conn:
        q = f"INSERT INTO car VALUES ('{carID}', '{carLat}', '{carLong}', '{make}', '{model}', '{year}', '{VIN}', '{owner_id}')"
        conn.execute(q)

def update_car(carID, carLat, carLong, make, model, year, VIN, owner_id):
    with db.begin() as conn:
        q = f"UPDATE car SET car_lat='{carLat}', car_lon='{carLong}', make='{make}', model='{model}', year='{year}', VIN='{VIN}', owner_id='{owner_id}' WHERE car_id='{carID}'"
        conn.execute(q)

def delete_car(carID):
    with db.begin() as conn:
        q = f"DELETE FROM car WHERE car_id='{carID}'"
        conn.execute(q)

# This function inserts data about car availability into the carAvailability table
def insert_car_availability(avail_id, carID, availability_from, availability_till):
    with db.begin() as conn:
        q = f"INSERT INTO carAvailability VALUES ('{avail_id}', '{carID}', '{availability_from}', '{availability_till}')"
        conn.execute(q)

# This updates car availability in the car availability table
def update_car_availability(carID, avail_from, avail_till):
    with db.begin() as conn:
        q = f"UPDATE carAvailability SET availability_from='{avail_from}', availability_till='{avail_till}' WHERE car_id='{carID}'"
        conn.execute(q)

# For Historical Trips
# This may not necessarily be needed
def historical_trips():
    # Show past histories of cars that were rented out
    conn = db.connect()
    q = """
    SELECT 
		car.car_id, 
        make, 
        model, 
        year,
        price,
        rating,
        pickup_datetime, dropoff_datetime
	FROM carTripHistory 
	JOIN car ON car.car_id = carTripHistory.car_id
    """
    res = conn.execute(q)
    return [r for r in res]

# TRIGGER FUNCTION
# This deletes a car from the carAvailabilities table
# def trigger(journeyID, lesserID, carID, availID, pickup_time, dropoff_time):
#     with db.begin() as conn:
#     #conn = db.connect()
#     # q1 = conn.execute(f"SELECT availability_id, car_id, availability_from, availability_till FROM carAvailability")

#     # if q1 is not None:
#     #     return False

#     # avail_id, car_id, pickuptime, dropofftime = q1

#     # if avail_id == 0:
#     #     return False
    
#     # Insert Into the CarTripHistorytable
#         q1 = f"Insert INTO carTripHistory VALUES ('{journeyID}', '{lesserID}', '{carID}', '{pickup_time}', '{dropoff_time}', NULL, NULL)"
#         conn.execute(q1)
#         # q = f"DELETE FROM carAvailability WHERE availability_id='{availID}'"
#         # conn.execute(q)

# def insert_into_car_trip_history(journey_id, lesser_id, car_id, pickup_datetime, dropoff_datetime, price, rating):
#     with db.begin() as conn:
#         q = f"INSERT INTO carTripHistory VALUES ('{journey_id}', '{lesser_id}', '{car_id}', '{pickup_datetime}', '{dropoff_datetime}')"
#         conn.execute(q)

# Stuff for trigger
def insert_into_your_bookings(car_booking_id, first_name, last_name, lesser_id, pickup_time, dropoff_time):
    with db.begin() as conn:
        q = f"INSERT INTO carBookings VALUES ('{car_booking_id}', '{first_name}', '{last_name}', '{lesser_id}', '{pickup_time}', '{dropoff_time}')"
        conn.execute(q)

def delete_availability(avail_id):
    with db.begin() as conn:
        q = f"DELETE FROM carAvailability WHERE availability_id='{avail_id}'"
        conn.execute(q)

# Stored Procedure to validate booking
def is_car_rentable(user_id, start_dt, end_dt):
    with db.begin() as conn:
        q = f"CALL TripHistClash('{user_id}', '{start_dt}', '{end_dt}', @rentable, @fRide)"
        conn.execute(q)
        res = conn.execute("SELECT @rentable, @fRide").fetchone()
    is_rentable, is_freeRide = res
    return is_rentable, is_freeRide
 
