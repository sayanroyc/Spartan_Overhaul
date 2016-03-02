from flask import Flask,request,json,jsonify,Response,abort
import global_vars
from google.appengine.ext import ndb
from google.appengine.api import search
from gcloud import storage
from models import User,Listing
from error_handlers import InvalidUsage

app = Flask(__name__)


# TODO: write functions for getting listings when a user is not logged in


# Calculate some similarity score ranking
# Maybe try to calculate the probability that the user will rent/enjoy/be-interested-in this item 
# TODO: What are we trying to optimize with this score? The probability of rental or enjoyment or depends?
# Maybe for new users, we try to find the probability that the user will rent. So the first items they see are the ones they're most likely to rent
# For exisiting users who have built some trust with the system, maybe more value is found through discovery of new items?
# Tons of experimentation and exploring to do here... This will make/break the entire app

# This partial snapshots function will be displayed when the user first opens the app
# In the future, we want to display recommended categories of listings that the user might like
# This function will be replaced, but need something for the MVP..

NumListingsToReturn = 200		# Search will return up to 200 listings

@app.route('/advertised_listings/snapshots/user_id=<int:user_id>/radius=<int:radius_miles>')
def get_advertised_listings_partial_snapshots(user_id, radius_miles):
	# Get the user
	u = User.get_by_id(user_id)
	if u is None:
		raise InvalidUsage('UserID does not match any existing user', status_code=400)

	# Calculate radius in meters
	radius_meters = radius_miles*METERS_PER_MILE

	# Get all of the Listings local to the current user
	query_string = 'distance(location, geopoint('+str(u.last_known_location.lat)+','+str(u.last_known_location.lon)+')) < '+str(radius_meters)+' AND NOT owner_id='+str(user_id)

	listing_ids, num_results = get_matched_listings_ids(query_string)

	resp 			 = jsonify({'num_results':num_results,'listing_ids':listing_ids})
	resp.status_code = 200
	return resp




# This function returns listings IDs whose names match part of the search string sent by the user
@app.route('/advertised_listings/user_id=<int:user_id>/radius=<int:radius_miles>/search=<search_string>')
def search_advertised_listings(user_id, radius_miles, search_string):
	# Get the user
	u = User.get_by_id(user_id)
	if u is None:
		raise InvalidUsage('UserID does not match any existing user', status_code=400)

	# Calculate radius in meters
	radius_meters = radius_miles*METERS_PER_MILE

	
	query_string = 'distance(location, geopoint('+str(u.last_known_location.lat)+','+str(u.last_known_location.lon)+')) < '+str(radius_meters)+' AND NOT owner_id='+str(user_id)+' AND name: '+search_string

	listing_ids, num_results = get_matched_listings_ids(query_string)

	resp 			 = jsonify({'num_results':num_results,'listing_ids':listing_ids})
	resp.status_code = 200
	return resp




# This function returns snapshot data given a listing_id
@app.route('/advertised_listings/snapshot/listing_id=<int:listing_id>')
def get_listing_snapshot(listing_id):
	l = Listing.get_by_id(listing_id)
	if l is None:
		raise InvalidUsage('Listing does not exist!', status_code=400)

	listing_img_media_links = get_listing_images(listing_id)

	# Add function for related items?

	# Return the attributes of the new item
	# Figure out what we want to send in a snapshot..
	listing_data = {'name':l.name,'rating':l.rating,'hourly_rate':l.hourly_rate,
					'daily_rate':l.daily_rate,'weekly_rate':l.weekly_rate,
					'image_media_links':listing_img_media_links}

	resp = jsonify(listing_data)
	resp.status_code = 200
	return resp





# Helper function that returns a list of listing_ids info given a a query_string
def get_matched_listings_ids(query_string):
	index = search.Index(name='Listing')
	try:
		results = index.search(search.Query(query_string=query_string,
						options=search.QueryOptions(limit=NumListingsToReturn, ids_only=True)))
	except search.Error:
		abort(500)

	listing_ids = []
	for matched_listing in results:
		listing_ids += [int(matched_listing.doc_id)]

	num_results = results.number_found if results.number_found < NumListingsToReturn else NumListingsToReturn

	return listing_ids, num_results




# Helper function to calculate distance from one location to another
# Move this some place else..
# Should connect listings.py and search.py into one, add this function to it
METERS_PER_MILE = 1609.344
EARTH_RADIUS = 6378135 			# meters
def haversine(lat1, lon1, lat2, lon2):
	dLat = radians(lat2 - lat1)
	dLon = radians(lon2 - lon1)
	lat1 = radians(lat1)
	lat2 = radians(lat2)

	a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
	c = 2*asin(sqrt(a))
	return EARTH_RADIUS * c / METERS_PER_MILE


# Helper function to return a listing's image links
def get_listing_images(listing_id):	
	client = storage.Client()
	bucket = client.get_bucket(global_vars.LISTING_IMG_BUCKET)

	listing_img_objects = bucket.list_blobs(prefix=str(listing_id))
	listing_img_media_links = []
	for img_object in listing_img_objects:
		listing_img_media_links += [img_object.media_link]

	return listing_img_media_links




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

