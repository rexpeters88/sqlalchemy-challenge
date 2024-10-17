# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

# Home Route
@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data as JSON."""
    # Find the most recent date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).first()[0]

    # Calculate the date one year ago from the most recent date
    most_recent_datetime = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_datetime - dt.timedelta(days=365)

    # Query for the last 12 months of precipitation data
    precip_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    # Convert the query results to a dictionary using date as the key and prcp as the value
    precip_dict = {date: prcp for date, prcp in precip_data}

    # Return the JSON representation of the dictionary
    return jsonify(precip_dict)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of all stations."""
    # Query all stations
    station_results = session.query(Station.station).all()

    # Convert the query results into list
    stations_list = list(np.ravel(station_results))

    # Return JSON representation of the stations
    return jsonify(stations_list)



# Temperature observations (tobs) route for most active station
@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature observations for the most active station for the last year."""

    # ID most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    # Calculate date one year ago from most recent date in dataset
    most_recent_date = session.query(func.max(Measurement.date)).first()[0]
    most_recent_datetime = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_datetime - dt.timedelta(days=365)

    # Query temp observations for last year for the most active station
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    # Convert the query results into a list
    temp_list = list(np.ravel(temperature_data))

    # Return JSON representation of temperature observations
    return jsonify(temp_list)


# Dynamic route for start date only
@app.route("/api/v1.0/<start>")
def temp_stats_start(start):
    """Return the min, avg, and max temperatures for all dates greater than or equal to the start date."""
    # Query min, avg, and max temperatures from the start date onwards
    temp_stats = session.query(func.min(Measurement.tobs), 
                               func.avg(Measurement.tobs), 
                               func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Convert  query result to list
    temp_stats_list = list(np.ravel(temp_stats))

    # Return  JSON of the temperature stats
    return jsonify(temp_stats_list)

# Dynamic route for start and end date
@app.route("/api/v1.0/<start>/<end>")
def temp_stats_start_end(start, end):
    """Return the min, avg, and max temperatures for all dates between the start and end date."""
    # Query min, avg, and max temperatures between the start and end dates
    temp_stats = session.query(func.min(Measurement.tobs), 
                               func.avg(Measurement.tobs), 
                               func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    # Convert the query result into list
    temp_stats_list = list(np.ravel(temp_stats))

    # Return JSON of the temperature stats
    return jsonify(temp_stats_list)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)