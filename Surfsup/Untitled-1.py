
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Correct path for the SQLite database
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect the database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Print available table names detected by SQLAlchemy
print(Base.classes.keys())