import numpy as np

import sqlalchemy
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
def home_page():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"Date format: ####-##-## (year-mo-day)<br/>"
        f"Date range: 2010-01-01 to 2017-08-23<br/>"
        f"/api/v1.0/(start date)<br/>"
        f"/api/v1.0/(start date)/(end date)<br/>"
        f"<br/>"     
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a Dictionary using `date` as the key and `prcp` as the value."""
    """Return the JSON representation of your dictionary."""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    last_12_mo_data = session.query(Measurement.date, Measurement.prcp).\
                    filter(Measurement.date >= '2016-08-23').\
                    order_by(Measurement.date).all()
    
    session.close()
    
    precip_dict = dict(last_12_mo_data)
    
    return jsonify(precip_dict)

    
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    session = Session(engine)
    
    station_names = session.query(Station.name)
    
    session.close()
    
    s_list = list(station_names)
    
    return jsonify(s_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """query for the dates and temperature observations from a year from the last data point."""
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""
    session = Session(engine)
    
    dt_tobs_lstyr = session.query(Measurement.date, Measurement.tobs).\
                              filter(Measurement.date >= '2016-08-23')
    
    session.close()
    
    dt_tobs_lstyr_dict = dict(dt_tobs_lstyr)
    
    return jsonify(dt_tobs_lstyr_dict)
    
@app.route("/api/v1.0/<start>")
def start_date(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date"""
    """When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date"""
    """Range of Dates: 2010-01-01 to 2017-08-23"""
    
    canonicalized = start.replace(" ", "-")
    
    #Check if input is in date range
    if (canonicalized > '2017-08-23') or (canonicalized < '2010-01-01'):
        return jsonify({"error": f"{canonicalized} is out of range."}), 404
    
    session = Session(engine)
    
    t_calcs = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= canonicalized).all()
    
    session.close()
    
    t_calcs_list = list(t_calcs)
    
    return jsonify(t_calcs_list)
    
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range"""
    """When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date 
    inclusive"""
    """Range of Dates: 2010-01-01 to 2017-08-23"""
    
    canonicalized_s = start.replace(" ", "-")
    canonicalized_e = end.replace(" ", "-")
    
    #Check if inputs are in date range
    if (canonicalized_s > '2017-08-23') or (canonicalized_s < '2010-01-01'):
        return jsonify({"error": f"{canonicalized_s} is out of range."}), 404
    
    if (canonicalized_e > '2017-08-23') or (canonicalized_e < '2010-01-01'):
        return jsonify({"error": f"{canonicalized_e} is out of range."}), 404
    
    if (canonicalized_s > canonicalized_e):
        return jsonify({"error": "Start date is after the end date."}), 404
   
    session = Session(engine)
    
    t_calcs = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= canonicalized_s).\
                        filter(Measurement.date <= canonicalized_e).all()
    
    session.close()
    
    t_calcs_list = list(t_calcs)
    
    return jsonify(t_calcs_list)

if __name__ == "__main__":
    app.run(debug=True)

















