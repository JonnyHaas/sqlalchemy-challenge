# Import the dependencies.
import numpy as np
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

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
# Import Flask
from flask import Flask, jsonify

# Create an app, being sure to pass __name__  (2 underscores each side of name)
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Routes direct where we want the code to run.
# / means execute the home page

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

# Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create a session link from Python to the database
    session = Session(engine)

    # Calculate the date one year from the last date in the database
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    date_one_year_ago = most_recent_date - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_one_year_ago).all()

    session.close()  # Close the session after the query

    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in results}

    return jsonify(precipitation_dict)


# Stations Route
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    # Query to get stations
    results = session.query(Station.station).all()

    session.close()

    # Convert results to a list
    stations = [station[0] for station in results]

    return jsonify(stations)


# Temperature Observations (TOBS) Route
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Query to find the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    # Calculate the date one year from the last date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    date_one_year_ago = most_recent_date - dt.timedelta(days=365)

    # Query the last 12 months of temperature observation data for the most active station
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= date_one_year_ago).all()

    session.close()

    # Convert results to a list
    temperatures = [temp[0] for temp in results]

    return jsonify(temperatures)


# Start and Start-End Range Routes
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start(start, end=None):
    session = Session(engine)

    if end:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    else:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()

    session.close()

    # Convert results to a dictionary
    temps = list(np.ravel(results))
    return jsonify(temps)


if __name__ == '__main__':
    app.run(debug=True)


