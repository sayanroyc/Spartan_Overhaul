from flask import Flask,request,json,jsonify,Response,abort
import datetime, time
from google.appengine.ext import ndb
from models import User,Listing,Meeting_Time,Meeting_Location,Meeting_Event,Rent_Event 
from error_handlers import InvalidUsage

app = Flask(__name__)


# Get a specific meeting event
@app.route('/meeting_event/get_meeting_event/meeting_event_id=<int:meeting_event_id>', methods=['GET'])
def get_meeting_event_info(meeting_event_id):
	e = Meeting_Event.get_by_id(meeting_event_id)
	meeting_id 				= str(e.key.id())
	owner_id 				= str(e.owner.id())
	renter_id 				= str(e.renter.id())
	listing_id 				= str(e.listing.id())
	deliverer 				= e.deliverer
	status 					= e.status

	proposed_meeting_location_ids = []
	for l in e.proposed_meeting_locations:
		proposed_meeting_location_ids += [str(l.id())]

	proposed_meeting_times_data = []
	for t in e.proposed_meeting_times:
		time_str 		= t.time.strftime("%Y %m %d %H:%M:%S")
		duration 		= float(t.duration)
		is_available 	= bool(t.is_available)
		time_data 		= {'time':time_str, 'duration':duration, 'is_available':is_available}
		proposed_meeting_times_data += [time_data]

	time = None
	if e.time is not None:
		time = e.time.strftime("%Y %m %d %H:%M:%S")

	location_id = None
	if e.location is not None:
		location_id = str(e.location.id())

	owner_confirmation_time = None
	if e.owner_confirmation_time is not None:
		owner_confirmation_time = e.owner_confirmation_time.strftime("%Y %m %d %H:%M:%S")

	renter_confirmation_time = None
	if e.renter_confirmation_time is not None:
		renter_confirmation_time = e.renter_confirmation_time.strftime("%Y %m %d %H:%M:%S")

	data = {'meeting_id':meeting_id, 'owner_id':owner_id, 'renter_id':renter_id, 'listing_id':listing_id, 'deliverer':deliverer, 'status':status, 'proposed_meeting_location_ids':proposed_meeting_location_ids, 'proposed_meeting_times_data':proposed_meeting_times_data, 'time':time, 'location_id':location_id, 'owner_confirmation_time':owner_confirmation_time, 'renter_confirmation_time':renter_confirmation_time}

	resp = jsonify(data)
	resp.status_code = 200
	return resp




# MARK: - Meeting Events
@app.route('/meeting_event/get_user_meeting_events/user_id=<int:user_id>', methods=['GET'])
def get_user_meeting_events(user_id):
	u_key = ndb.Key('User', user_id)

	# qry 			= Meeting_Event.query(ndb.OR(Meeting_Event.owner == u_key, Meeting_Event.renter == u_key), ndb.OR(Meeting_Event.status == 'Proposed', Meeting_Event.status == 'Scheduled', Meeting_Event.status == 'Delayed'))
	# qry 			= Meeting_Event.query(ndb.OR(Meeting_Event.owner == u_key, Meeting_Event.renter == u_key))
	qry 			= Meeting_Event.query(Meeting_Event.owner == u_key)
	meeting_events 	= qry.fetch()

	data = []
	for e in meeting_events:
		meeting_id 				= str(e.key.id())
		owner_id 				= str(e.owner.id())
		renter_id 				= str(e.renter.id())
		listing_id 				= str(e.listing.id())
		deliverer 				= e.deliverer
		status 					= e.status

		proposed_meeting_location_ids = []
		for l in e.proposed_meeting_locations:
			proposed_meeting_location_ids += [str(l.id())]

		proposed_meeting_times_data = []
		for t in e.proposed_meeting_times:
			time_str 		= t.time.strftime("%Y %m %d %H:%M:%S")
			duration 		= float(t.duration)
			is_available 	= bool(t.is_available)
			time_data 		= {'time':time_str, 'duration':duration, 'is_available':is_available}
			proposed_meeting_times_data += [time_data]

		time = None
		if e.time is not None:
			time = e.time.strftime("%Y %m %d %H:%M:%S")

		location_id = None
		if e.location is not None:
			location_id = str(e.location.id())

		owner_confirmation_time = None
		if e.owner_confirmation_time is not None:
			owner_confirmation_time = e.owner_confirmation_time.strftime("%Y %m %d %H:%M:%S")

		renter_confirmation_time = None
		if e.renter_confirmation_time is not None:
			renter_confirmation_time = e.renter_confirmation_time.strftime("%Y %m %d %H:%M:%S")
		
		event_data = {'meeting_id':meeting_id, 'owner_id':owner_id, 'renter_id':renter_id, 'listing_id':listing_id, 'deliverer':deliverer, 'status':status, 'proposed_meeting_location_ids':proposed_meeting_location_ids, 'proposed_meeting_times_data':proposed_meeting_times_data, 'time':time, 'location_id':location_id, 'owner_confirmation_time':owner_confirmation_time, 'renter_confirmation_time':renter_confirmation_time}
		data += [event_data]

	resp = jsonify({'events':data})
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