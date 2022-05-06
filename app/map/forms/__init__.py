from flask_wtf import FlaskForm
from wtforms import validators
from wtforms.fields import *

class csv_upload(FlaskForm):
    file = FileField()
    submit = SubmitField()
    
    
class edit_location_form(FlaskForm):
    title= TextAreaField('Title', description="Please change the title")
    population= TextAreaField('Population', description="Please update the population")
    
    submit= SubmitField()
    
class add_location_form(FlaskForm):
    title= TextAreaField('Title', [validators.DataRequired()], description="Please enter the name of the location")
    longitude= TextAreaField('Longitude', [validators.DataRequired()], description="Please enter the longitude of the location")
    latitude= TextAreaField('Latitude', [validators.DataRequired()], description="Please enter the latitude of the location")
    population= TextAreaField('Population', [validators.DataRequired()], description="Please add the population")
    submit= SubmitField()