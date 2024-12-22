# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from datetime import datetime, timedelta


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
@app.route("/")
def welcome():
    """Homepage listing all available routes"""
    return (
        f"Welcome to the Climate App API!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )



#################################################
# Flask Routes
#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data"""
    # Calculate the date one year ago from the last data point
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - timedelta(days=365)

    # Query for date and precipitation
    precipitation_query = session.query(Measurement.date, Measurement.prcp).filter(
        Measurement.date >= one_year_ago
    ).all()

    # Convert query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in precipitation_query}

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations"""
    station_query = session.query(Station.station).all()
    stations = [station[0] for station in station_query]

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the last 12 months of temperature observations for the most active station"""
    # Calculate the date one year ago from the last data point
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - timedelta(days=365)

    # Identify the most active station
    most_active_station = (
        session.query(Measurement.station)
        .group_by(Measurement.station)
        .order_by(func.count(Measurement.station).desc())
        .first()[0]
    )

    # Query the temperature observations for the most active station
    tobs_query = session.query(Measurement.tobs).filter(
        Measurement.station == most_active_station, Measurement.date >= one_year_ago
    ).all()

    tobs_data = [tobs[0] for tobs in tobs_query]

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start, end=None):
    """Return TMIN, TAVG, and TMAX for the specified start or start-end range"""
    # Convert start and end dates to datetime objects
    start_date = datetime.strptime(start, "%Y-%m-%d")
    if end:
        end_date = datetime.strptime(end, "%Y-%m-%d")
    else:
        end_date = session.query(func.max(Measurement.date)).scalar()
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # Query for TMIN, TAVG, and TMAX
    temperature_query = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs),
    ).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

    temperature_data = {
        "Start Date": start,
        "End Date": end if end else "Latest",
        "TMIN": temperature_query[0][0],
        "TAVG": temperature_query[0][1],
        "TMAX": temperature_query[0][2],
    }

    return jsonify(temperature_data)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
