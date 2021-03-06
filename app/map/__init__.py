import csv
import json
import logging
import os

from flask import Blueprint, render_template, abort, url_for, current_app, jsonify, flash
from flask_login import current_user, login_required
from jinja2 import TemplateNotFound

from app.db import db
from app.db.models import Location
from app.songs.forms import csv_upload
from app.map.forms import csv_upload, edit_location_form, add_location_form
from werkzeug.utils import secure_filename, redirect
from flask import Response

map = Blueprint('map', __name__,
                        template_folder='templates')

@map.route('/locations', methods=['GET'], defaults={"page": 1})
@map.route('/locations/<int:page>', methods=['GET'])
def browse_locations(page):
    page = page
    per_page = 10
    pagination = Location.query.paginate(page, per_page, error_out=False)
    data = pagination.items
    edit_location = ('map.edit_location', [('locations_id', ':id')])
    add_location = url_for('map.add_location')
    delete_location = ('map.delete_location', [('locations_id', ':id')])

    try:
        return render_template('browse_locations.html', data=data,pagination=pagination, Location=Location,
                               edit_location=edit_location, add_location=add_location, delete_location=delete_location)
    except TemplateNotFound:
        abort(404)

@map.route('/locations_datatables/', methods=['GET'])
def browse_locations_datatables():

    data = Location.query.all()

    try:
        return render_template('browse_locations_datatables.html',data=data)
    except TemplateNotFound:
        abort(404)

@map.route('/locations/<int:locations_id>/edit', methods=['POST','GET'])
@login_required
#allows users to edit title and population for Locations
def edit_location(locations_id):
    location = Location.query.get(locations_id)
    form = edit_location_form(obj=location)
    if form.validate_on_submit():
        location.population = form.population.data
        location.title = form.title.data
        db.session.add(location)
        db.session.commit()
        flash('Location Updated Successfully', 'success')
        current_app.logger.info("edited a user")
        return redirect(url_for('map.browse_locations'))
    return render_template('edit_locations.html', form=form)

@map.route('/locations/new', methods=['POST','GET'])
@login_required
def add_location():
    form = add_location_form()
    if form.validate_on_submit():
        new_location = Location.query.filter_by(title=form.title.data).first()
        if new_location is None:
            new_location = Location(title=form.title.data, longitude=form.longitude.data, latitude=form.latitude.data, population= form.population.data)
            db.session.add(new_location)
            db.session.commit()
            flash('Congratulations, you just added a new location', 'success')
            return redirect(url_for('map.browse_locations'))
        else:
            flash('This Location already exists')
            return redirect(url_for('auth.browse_locations'))
    return render_template('add_location.html', form=form)


@map.route('/locations/<int:locations_id>/delete', methods=['POST'])
@login_required
#deletes locations from database
def delete_location(locations_id):
    locations_id = Location.query.get(locations_id)
    db.session.delete(locations_id)
    db.session.commit()
    flash('Location Deleted', 'success')
    return redirect(url_for('map.browse_locations'))


@map.route('/api/locations/', methods=['GET'])
def api_locations():
    data = Location.query.all()
    try:
        return jsonify(data=[location.serialize() for location in data])
    except TemplateNotFound:
        abort(404)


@map.route('/locations/map', methods=['GET'])
def map_locations():
    google_api_key = current_app.config.get('GOOGLE_API_KEY')
    try:
        return render_template('map_locations.html',google_api_key=google_api_key)
    except TemplateNotFound:
        abort(404)



@map.route('/locations/upload', methods=['POST', 'GET'])
@login_required
def location_upload():
    form = csv_upload()
    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        form.file.data.save(filepath)
        list_of_locations = []
        with open(filepath) as file:
            csv_file = csv.DictReader(file)
            for row in csv_file:
                location = Location.query.filter_by(title=row['location']).first()
                if location is None:
                    current_user.locations.append(Location(row['location'],row['longitude'],row['latitude'],row['population']))
                    db.session.commit()
                else:
                    current_user.locations.append(location)
                    db.session.commit()
        return redirect(url_for('map.browse_locations'))

    try:
        return render_template('upload_locations.html', form=form)
    except TemplateNotFound:
        abort(404)