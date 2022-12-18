from app import app
from app import database as db_helper

from flask import render_template, request, session, redirect

from app.utils import render_template_with_nav
import app.user as user

import random 
import pickle
import json

def homepage():
    return redirect("/search_cars")

@app.route('/register', methods=['post','get'])
def register():
    error=None
    success=None
    if request.method == 'POST':
        firstname = request.form.get('firstName')
        lastname = request.form.get('lastName')
        email = request.form.get('email')
        is_leasor = request.form.get('is_leasor')
        password = request.form.get('password')
        confirmpassword = request.form.get('confirmpassword')

        if len(firstname) < 2: 
            error = "Firstname is too short"
        elif len(password) < 6:
            error = "Password is too short"
        elif password != confirmpassword:
            error = "Passwords do not match"
        if not error:
            user.create_user(firstname, lastname, is_leasor, email, password)
            success = "Your account has been created"

    return render_template('register.html',error=error,msg=success)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.args.get("logout", default=False, type=bool):
        user.logout()
        return render_template("login.html")
    email=request.form.get('email')
    password = request.form.get('password')
    u = user.login(email, password)
    if u is None:
        return render_template('login.html')
    if 'current_url' in session:
        return redirect(session.get('current_url'))
    return homepage()

def check_login(url):
    if user.get_current_user_id() is None:
        session['current_url'] = url
        return redirect("/login")
    return None


@app.route("/")
def base():
    if user.get_current_user_id() is not None:
        return homepage()
    return login()

@app.route("/top_charts")
def top_charts():
    data = {}
    data["top_rated_cars"] = db_helper.advanced_query_top_rated_cars()
    data["new_users"] = db_helper.advanced_query_new_cars_without_trips()
    return render_template_with_nav("top_charts.html", **data)


@app.route("/historical_trips", methods=['GET', 'POST'])
def historical_trips():
    reload = check_login(request.path)
    if reload:
        return reload
    my_trips = db_helper.get_your_trip_history(user_id=user.get_current_user_id())
    data = {"my_trips":my_trips}
    return render_template_with_nav("historical_trips.html", **data)


@app.route("/search_cars", methods=['GET', 'POST'])
def search_cars():
    reload = check_login(request.path)
    if reload:
        return reload
    data = {}
    if request.method == "POST":
        pic_lat = float(request.values['pickup_lat'])
        pic_lon = float(request.values['pickup_lon'])
    
        pic_dt = str(request.values['pickup-time']).replace('T', ' ')
        drop_dt = str(request.values['dropoff-time']).replace('T', ' ')
        is_make = 'isMake' in request.form
        is_year = 'isYear' in request.form
        make, year = None, None
        if is_make:
            make = request.values['make']
        if is_year:
            year = request.values['year']
        car, prices = db_helper.fetch_car(pic_lat, pic_lon, pic_dt, drop_dt, \
                                        is_make, is_year, make, year)
        data["avail_cars"] = car
        data["all_prices"] = prices
    print(data)

    return render_template_with_nav("search_cars.html", **data)

@app.route("/create_car", methods=['post','get'])
def create_car():
    error=None
    success=None
    #owner_id = user.get_current_user_id() 
    if request.method == 'POST':
        carID = request.form.get('carID')
        carLat = float(request.form.get('carLat'))
        carLong = float(request.form.get('carLong'))
        make = request.form.get('make')
        model = request.form.get('model')
        year = request.form.get('year')
        VIN = request.form.get('vin')

        # For carAvailability table
        avail_from = str(request.values['pickup-time']).replace('T', ' ')
        avail_till = str(request.values['dropoff-time']).replace('T', ' ')

        #owner_id = user.get_current_user_id()
        avail_id = random.randint(11707, 20000)

        if len(carID) < 10: 
            error = "Car Id is too short"
        # elif len(VIN) == 17:
        #     error = "Enter your correct 17 digit VIN!"
        print('Success')
        if not error:
            #add_car will not work if the foreign key user / owner_id is not set in the database
            db_helper.add_car(carID, carLat, carLong, make, model, year, VIN, "031fea9628f9238b051a58808554498a")
            db_helper.insert_car_availability(avail_id, carID, avail_from, avail_till)
            success = "Your car has been added to the listings!"
    return render_template("create_car.html",error=error,msg=success)


@app.route("/update_car", methods=['GET', 'POST'])
def update_car():
    error=None
    success=None
    #owner_id = user.get_current_user_id() 
    if request.method == 'POST':
        carID = request.form.get('carID')
        carLat = float(request.form.get('carLat'))
        carLong = float(request.form.get('carLong'))
        make = request.form.get('make')
        model = request.form.get('model')
        year = request.form.get('year')
        VIN = request.form.get('vin')

        #owner_id = user.get_current_user_id()
        avail_from = str(request.values['pickup-time']).replace('T', ' ')
        avail_till = str(request.values['dropoff-time']).replace('T', ' ')

        if len(carID) < 10: 
            error = "Car Id is too short"
        # elif len(VIN) == 17:
        #     error = "Enter your correct 17 digit VIN!"
        print('Success')
        if not error:
            #update_car will not work if the foreign key user / owner_id is not set in the database
            db_helper.update_car(carID, carLat, carLong, make, model, year, VIN, "031fea9628f9238b051a58808554498a")

            # Updates car availability times
            db_helper.update_car_availability(carID, avail_from, avail_till)

            success = "Your car has been updated!"
    return render_template("update_car.html",error=error,msg=success)

@app.route("/delete_car", methods=['post','get'])
def delete_car():
    error=None
    success=None
    #owner_id = user.get_current_user_id() 
    if request.method == 'POST':
        carID = request.form.get('carID')
        print('Success')
        if not error:
            db_helper.delete_car(carID)
            success = "Your car has been deleted from the listings!"
    return render_template("delete_car.html",error=error,msg=success)

@app.route("/rent_car", methods=['post','get'])
def rent_car():
    error=None
    success=None

    owner_id = user.get_current_user_id() 
    if request.method == 'POST':
        carID = request.form.get('carID') 
        availabilityID = request.form.get('carAvailabilityID')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        lesser_id = request.form.get('lesserID')
        avail_from = str(request.values['pickup-time']).replace('T', ' ')
        avail_till = str(request.values['dropoff-time']).replace('T', ' ')

        car_booking_id = random.randint(0, 9999)
        
        is_rentable, is_free_ride = db_helper.is_car_rentable(owner_id, avail_from, avail_till)
        if not is_rentable:
            error = "You cannot rent this car, please check you timings!"
            
        if not error:
            db_helper.insert_into_your_bookings(car_booking_id, first_name, last_name, lesser_id, avail_from, avail_till)
            db_helper.delete_availability(availabilityID)
            if is_free_ride:
                success = "You have successfully rented the car with a free ride!"
            else:
                success = "You have successfully rented the car!"
    return render_template("rent_car.html",error=error,msg=success)

@app.route("/car_trip_history", methods=['post','get'])
def car_trip_history():
    data = {}
    data["car_history"] = db_helper.historical_trips()
    return render_template_with_nav("car_trip_history.html", **data)
