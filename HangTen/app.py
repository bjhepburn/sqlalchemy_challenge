# Import Dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify, request
import numpy as np
import pandas as pd
import datetime as dt
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the 'Hang Ten' API!<br/><br/>"

        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    query_date = dt.date(2017,8,23) - dt.timedelta(days = 365)
    recent_12_months = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= query_date).all()
    year = list(np.ravel(recent_12_months))
    return jsonify(year)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    island_stations = session.query(Measurement.station).distinct()
    isle_stations = [station[0] for station in island_stations]
    return jsonify(isle_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    query_date = dt.date(2017,8,23) - dt.timedelta(days = 365)

    active_station = session.query(Measurement.station, func.count(Measurement.station))\
    .group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()[0][0]

    station_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == active_station).\
    filter(Measurement.date >= query_date).group_by(Measurement.tobs).all()

    tobs_list = list(np.ravel(station_tobs))

    return jsonify(tobs_list)

@app.route("/api/v1.0/<path:date>")
def start(date):
    session = Session(engine)
    data ={}
    data['min'] = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= date).all()[0][0]
    data['max'] = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= date).all()[0][0]
    data['avg'] = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= date).all()[0][0]
    return jsonify(data)

@app.route("/api/v1.0/<date>/<end_date>")
def range(date, end_date):
    session = Session(engine)
    data ={}
    data['min'] = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= date).filter(Measurement.date <= end_date).all()[0][0]
    data['max'] = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= date).filter(Measurement.date <= end_date).all()[0][0]
    data['avg'] = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= date).filter(Measurement.date <= end_date).all()[0][0]
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)