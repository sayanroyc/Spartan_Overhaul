from flask import Flask,request,json,jsonify,Response,abort
import datetime, time
from google.appengine.ext import ndb
from models import User,MeetingLocation
from error_handlers import InvalidUsage

app = Flask(__name__)

# Create a new meeting location object and put into Datastore
@app.route('/meeting_location/create/user_id=<int:user_id>', methods=['POST'])
def create_meeting_location(user_id):
	json_data 		 = request.get_json()
	google_places_id = json_data.get('google_places_id','')
	address 		 = json_data.get('address','')
	name 			 = json_data.get('name','')
	is_private 		 = bool(json_data.get('is_private',''))

	u = User.get_by_id(user_id)
	if u is None:
		raise InvalidUsage('UserID does not match any existing user', status_code=400)

	u_key = ndb.Key('User', user_id)

	l = MeetingLocation(user=u_key, google_places_id=google_places_id, address=address, 
						name=name, is_private=is_private)

	try:
		location_key = l.put()
	except:
		abort(500)

	data = {'location_id':location_key.id(), 'date_created':l.date_created, 'date_last_modified':l.date_last_modified}
	resp = jsonify(data)
	resp.status_code = 201
	return resp



# Delete a meeting location object
@app.route('/meeting_location/delete/location_id=<int:location_id>', methods=['DELETE'])
def delete_meeting_location(location_id):
	try:
		ndb.Key('MeetingLocation', location_id).delete()
	except:
		abort(500)

	now = datetime.datetime.now()

	data = {'location_id':location_id, 'date_deleted':now}
	resp = jsonify(data)
	resp.status_code = 200
	return resp




# Update a meeting location object
@app.route('/meeting_location/update/location_id=<int:location_id>', methods=['POST'])
def update_meeting_location(location_id):
	json_data 		 = request.get_json()
	google_places_id = json_data.get('google_places_id','')
	address 		 = json_data.get('address','')
	name 			 = json_data.get('name','')
	is_private 		 = bool(json_data.get('is_private',''))

	l = MeetingLocation.get_by_id(location_id)
	if l is None:
		raise InvalidUsage('LocationID does not match any existing location.', status_code=400)

	l.google_places_id 	= google_places_id
	l.address 			= address
	l.name 				= name
	l.is_private		= is_private

	try:
		location_key = l.put()
	except:
		abort(500)

	data = {'location_id':location_key.id(), 'date_created':l.date_created, 'date_last_modified':l.date_last_modified}
	resp = jsonify(data)
	resp.status_code = 200
	return resp




# Get a user's meeting locations
@app.route('/meeting_location/get_meeting_locations/user_id=<int:user_id>', methods=['GET'])
def get_user_meeting_locations(user_id):
	u = User.get_by_id(user_id)
	if u is None:
		raise InvalidUsage('User ID does not match any existing user', 400)

	u_key	= ndb.Key('User', user_id)
	qry 	= MeetingLocation.query(MeetingLocation.user == u_key)
	listings = qry.fetch()

	data = []
	for l in listings:
		listing_data = {'location_id':l.key.id(), 'name':l.name, 'google_places_id':l.google_places_id,
						'address':l.address, 'is_private':l.is_private}
		data += [listing_data]

	resp = jsonify({'meeting locations':data})
	resp.status_code = 200
	return resp



### Server Error Handlers ###
@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
	response = jsonify(error.to_dict())
	response.status_code = error.status_code
	return response

@app.errorhandler(404)
def page_not_found(e):
	"""Return a custom 404 error."""
	return 'Sorry, Nothing at this URL.', 404

@app.errorhandler(500)
def application_error(e):
	"""Return a custom 500 error."""
	return 'Sorry, unexpected error: {}'.format(e), 500