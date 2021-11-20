import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

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
def home(): 
    return(
        f"Welcome to Climate App<br/>"
        f"Available Routes: <br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"summary temperature data with from start date. Please add date with format yyyy-mm-dd <br/>"
        f"/api/v1.0/start<br/>"
        f"summary temperature data with from start and end date. Please add date with format yyyy-mm-dd <br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    #Convert the query results to a dictionary using date as the key and prcp as the value.
    prec_dict = {}
    for date, prcp in results: 
        prec_dict[date]=prcp
        
    #Return the JSON representation of your dictionary.
    return jsonify(prec_dict)

@app.route("/api/v1.0/stations")
def stations():
    #Return a JSON list of stations from the dataset.
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    station_list= []
    for station in results: 
        station_list.append(station[0])
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    #Query the dates and temperature observations of the most active station for the last year of data.
    session = Session(engine)
    date1=session.query(func.max(Measurement.date)).filter(Measurement.station == 'USC00519281').all()
    date1=date1[0][0]
    query_date = dt.datetime(2017,8,18) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').filter(Measurement.date>=query_date).all()
    session.close()
    tobs_list= []
    for tobs in results: 
        tobs_list.append(tobs[0])
    
    #Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(tobs_list)

"""Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""

@app.route("/api/v1.0/<start>")
def start(start):
    try: 
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
        session = Session(engine)
        results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start_date).all()
        session.close()
        summary_dict = {}
        summary_dict["Input Date"] = start
        summary_dict["TMIN"] = results[0][0]
        summary_dict["TMAX"] = results[0][1]
        summary_dict["TAVG"] = results[0][2]

        return jsonify(summary_dict)
    except: 
        return jsonify({"error": f"Invalid Date Format. Please enter date in yyyy-mm-dd format."}), 404
    

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
        end_date = dt.datetime.strptime(end, '%Y-%m-%d')
        session = Session(engine)
        results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date.between(start_date, end_date)).all()
        session.close()
        summary_dict = {}
        summary_dict["Start Date"] = start
        summary_dict["End Date"] = end
        summary_dict["TMIN"] = results[0][0]
        summary_dict["TMAX"] = results[0][1]
        summary_dict["TAVG"] = results[0][2]

        return jsonify(summary_dict)
    except: 
        return jsonify({"error": f"Invalid Date Format. Please enter date in yyyy-mm-dd format."}), 404

if __name__ == '__main__':
    app.run(debug=True)
