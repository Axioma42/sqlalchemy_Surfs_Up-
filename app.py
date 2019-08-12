from flask import Flask, jsonify, request
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
import numpy as np

engine = create_engine("sqlite:///hawaii.sqlite", echo=False, connect_args = {"check_same_thread":False})
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

minus_365 = dt.date(2017, 8, 23) - dt.timedelta(days=365)

app = Flask(__name__)

# List all routes that are available.
@app.route("/")
def home():
    return (
        "<h1>Hawaii Weather App</h1>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Convert the query results to a Dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():

    precipitation_api = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= minus_365).all()
    precipitation_dict = dict(precipitation_api)
    
    # Return the JSON representation of your dictionary.
    return jsonify(precipitation_dict)

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():

    stations_api = session.query(Measurement.station).group_by(Measurement.station).all()
    station_list = list(np.ravel(stations_api))
    return jsonify(station_list)

# Query for the dates and temperature observations from a year from the last data point.
@app.route("/api/v1.0/tobs")
def tobs():

    tobs_api = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= minus_365).all()
    tobs_list = list(tobs_api)
    # Return a JSON list of Temperature Observations (tobs) for the previous year.
    return jsonify(tobs_list)


# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>")
def start_date(start):
    
    start_api = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    start_list = list(start_api)
    return jsonify(start_list)


@app.route("/api/v1.0/<start>/<end>")
def start_to_end(start, end):

    start_to_end_api = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    start_to_end_list = list(start_to_end_api)
    return jsonify(start_to_end_list)

# Run the app.    
if __name__ == '__main__':
    app.run(debug = True)
