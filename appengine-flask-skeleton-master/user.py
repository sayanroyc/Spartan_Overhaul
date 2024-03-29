from flask import Flask,request,json,jsonify,Response,abort
import datetime, time
import global_vars
from google.appengine.ext import ndb
from google.appengine.api import search
from gcloud import storage
from models import User, Listing
from error_handlers import InvalidUsage

app = Flask(__name__)

# Create a new user object and put into Datastore and Search App
@app.route('/user/create', methods=['POST'])
def create_user():
	json_data 		= request.get_json()
	first_name 		= json_data.get('first_name','')
	last_name 		= json_data.get('last_name','')
	email 			= json_data.get('email','')
	phone_number 	= json_data.get('phone_number','')
	facebook_id		= json_data.get('facebook_id','')
	password 		= json_data.get('password','')
	signup_method 	= json_data.get('signup_method','')
	# location_lat 	= float(json_data.get('location_lat',''))
	# location_lon 	= float(json_data.get('location_lon',''))

	# TODO: get location from client


	# If object string is empty '', then set object = None
	if not bool(password):
		password = None
	if not bool(phone_number):
		phone_number = None
	if not bool(email):
		email = None		
	if not bool(facebook_id):
		facebook_id = None

	if signup_method != 'Facebook':
		if not phone_number:
			raise InvalidUsage('Phone number is required!', 400)
		if not password:
			raise InvalidUsage('Password is required!', 400)
	else:
		if not facebook_id:
			raise InvalidUsage('No facebook id given!', 400)
		

	# Validate password, email, and phone_number
	validate_password(password)
	validate_email(email)
	validate_phone(phone_number)


	# Create category weight vector
	# category_weights = []
	# categories = Category.query()
	# for cat in categories.iter():
	# 	cat_weight = CategoryWeight(category=cat.key, weight=1.0)
	# 	category_weights.append(cat_weight)


	# Add user to Datastore
	u = User(first_name=first_name, last_name=last_name, phone_number=phone_number, email=email, 
			 password=password, facebook_id=facebook_id, signup_method=signup_method)
	try:
		user_key = u.put()
		user_id  = str(user_key.id())
	except:
		abort(500)

	# Add user to Search App
	new_user = search.Document(
		doc_id=user_id,
		fields=[search.TextField(name='name', value=first_name+' '+last_name),
				search.TextField(name='phone_number', value=phone_number),
				search.TextField(name='email', value=email)])
	try:
		index = search.Index(name='User')
		index.put(new_user)
	except:
		abort(500)


	data = {'user_id':user_id, 'date_created':u.date_created, 'date_last_modified':u.date_last_modified}
	resp = jsonify(data)
	resp.status_code = 201
	return resp




# Delete a user object from Search API and set User status to 'Deactivated'
@app.route('/user/deactivate/user_id=<int:user_id>', methods=['DELETE'])
def deactivate_user(user_id):# Edit Datastore entity
	# Get the user
	u = User.get_by_id(user_id)
	if u is None:
		raise InvalidUsage('User ID does not match any existing user', 400)

	if u.status == 'Deactivated':
		raise InvalidUsage('User is already deactivated!', 400)

	# Set user status to 'Deactivated'
	u.status = 'Deactivated'

	# Set all of the user's listings to 'Deactivated'
	u_key = ndb.Key('User', user_id)
	qry = Listing.query(Listing.owner == u_key)
	listings = qry.fetch()
	for l in listings:
		if l.status != 'Deleted':
			l.status = 'Deactivated'
			try:
				l.put()
			except:
				abort(500)

	# Add the updated user status to the Datastore
	try:
		u.put()
	except:
		abort(500)


	# Delete Search App entity
	try:
		index = search.Index(name='User')
		index.delete(str(user_id))
	except:
		abort(500)


	# Return response
	data = {'user_id deactivated':user_id, 'date_deactivated':u.date_last_modified}
	resp = jsonify(data)
	resp.status_code = 200
	return resp




@app.route('/user/delete_from_search/user_id=<int:user_id>', methods=['DELETE'])
def delete_from_search(user_id):
	# Delete Search App entity
	try:
		index = search.Index(name='User')
		index.delete(str(user_id))
	except:
		abort(500)

	return 'User successfully deleted from Search App', 200




# Reactivate a user by adding it to Search API and set User status to 'Active'
@app.route('/user/reactivate/user_id=<int:user_id>', methods=['POST'])
def reactivate_user(user_id):
	# Get the user
	u = User.get_by_id(user_id)
	if u is None:
		raise InvalidUsage('User ID does not match any existing user', 400)

	if u.status == 'Active':
		raise InvalidUsage('User is already active!', 400)

	# Set user status to 'Active'
	u.status = 'Active'

	u.is_phone_number_verified = False
	u.is_email_verified = False
	
	first_name			= u.first_name 
	last_name			= u.last_name
	email				= u.email
	phone_number		= u.phone_number 
	date_created		= u.date_created

	# Add the updated user status to the Datastore
	try:
		u.put()
	except:
		abort(500)


	# Add reactivated user to the Search App
	reactivated_user = search.Document(
			doc_id=str(user_id),
			fields=[search.TextField(name='name', value=first_name+' '+last_name),
					search.TextField(name='phone_number', value=phone_number),
					search.TextField(name='email', value=email)])
	try:
		index = search.Index(name='User')
		index.put(reactivated_user)
	except:
		abort(500)


	data = {'user_id':user_id, 'date_created':date_created, 'date_last_modified':u.date_last_modified}
	resp = jsonify(data)
	resp.status_code = 201
	return resp




# Update a user's information
@app.route('/user/update/user_id=<int:user_id>', methods=['POST'])
def update_user(user_id):
	json_data 		= request.get_json()
	first_name 		= json_data.get('first_name','')
	last_name 		= json_data.get('last_name','')
	email 			= json_data.get('email','')
	phone_number 	= json_data.get('phone_number','')

	if not bool(first_name):
		raise InvalidUsage('First name cannot be left empty.', 400)
	if not bool(last_name):
		raise InvalidUsage('Last name cannot be left empty.', 400)
	if not bool(email):
		raise InvalidUsage('Email cannot be left empty.', 400)		
	if not bool(phone_number):
		raise InvalidUsage('Phone number cannot be left empty.', 400)


	# Get the user
	u = User.get_by_id(user_id)
	if u is None:
		raise InvalidUsage('User ID does not match any existing user', 400)

	# Validate email and phone number before updating anything
	if u.email != email:
		validate_email(email)
	if u.phone_number != phone_number:
		validate_phone(phone_number)

	# If the phone number is different, phone number is no longer verified 
	if phone_number != u.phone_number:
		u.is_phone_number_verified = False

	# If the email is different, email is no longer verified
	if email != u.email:
		u.is_email_verified = False
	
	# Update user attributes
	u.first_name 		 = first_name
	u.last_name 		 = last_name
	u.email 			 = email
	u.phone_number 		 = phone_number
	
	# Add the updated user to the Datastore
	try:
		u.put()
	except:
		abort(500)

	# Add updated user to the Search App
	updated_user = search.Document(
			doc_id=str(user_id),
			fields=[search.TextField(name='name', value=first_name+' '+last_name),
					search.TextField(name='phone_number', value=phone_number),
					search.TextField(name='email', value=email)])
	try:
		index = search.Index(name='User')
		index.put(updated_user)
	except:
		abort(500)

	# Return the fields of the new user
	data = {'first_name':first_name, 'last_name':last_name, 'phone_number':phone_number, 'is_phone_number_verified':u.is_phone_number_verified, 'email':email, 'is_email_verified':u.is_email_verified, 'date_last_modified':u.date_last_modified}
	resp = jsonify(data)
	resp.status_code = 200
	return resp




# Add/update a profile picture for a user
@app.route('/user/new_user_image/user_id=<int:user_id>', methods=['POST'])
def new_user_image(user_id):
	userfile = request.files['userfile']
	filename = userfile.filename

	# Check to see if the user exists
	u = User.get_by_id(user_id)
	if u is None:
		raise InvalidUsage('UserID does not match any existing user', status_code=400)

	# Create client for interfacing with Cloud Storage API
	client = storage.Client()
	bucket = client.get_bucket(global_vars.USER_IMG_BUCKET)

	# Calculating size this way is not very efficient. Is there another way?
	userfile.seek(0, 2)
	size = userfile.tell()
	userfile.seek(0)

	# Upload the user's profile image
	# image = bucket.blob(blob_name=str(user_id)+'/'+filename)
	# path = str(user_id)+'/profile_picture.jpg'
	path = str(user_id)+'/'+filename
	image = bucket.blob(blob_name=path)
	image.upload_from_file(file_obj=userfile, size=size, content_type='image/jpeg')

	# Hacky way of making our files public..
	image.acl.all().grant_read()
	image.acl.save()

	u.profile_picture_path = path
	u.put()

	resp = jsonify({'image_path':path, 'image_media_link':image.media_link})
	resp.status_code = 201
	return resp




# Delete a user's profile picture
@app.route('/user/delete_user_image/user_id=<int:user_id>', methods=['DELETE'])
def delete_user_image(user_id):
	# Check to see if the user exists
	u = User.get_by_id(user_id)
	if u is None:
		raise InvalidUsage('UserID does not match any existing user', status_code=400)

	path = u.profile_picture_path
	if path is None:
		raise InvalidUsage('User has no profile picture.', status_code=400)

	# Create client for interfacing with Cloud Storage API
	client = storage.Client()
	bucket = client.get_bucket(global_vars.USER_IMG_BUCKET)

	bucket.delete_blob(path)

	u.profile_picture_path = None
	u.put()

	now = datetime.datetime.now()

	# Return response
	resp = jsonify({'picture_id deleted':path, 'date_deleted':now})
	resp.status_code = 200
	return resp




# Get a user's public information
@app.route('/user/get_info/user_id=<int:user_id>', methods=['GET'])
def get_user_info(user_id):
	u = User.get_by_id(user_id)
	if u is None:
		raise InvalidUsage('User ID does not match any existing user', 400)

	# Get user data from Datastore
	first_name 			= u.first_name
	last_name 			= u.last_name
	phone_number 		= u.phone_number
	email 				= u.email
	path 				= u.profile_picture_path

	# Get user's profile picture
	if path != None:
		client = storage.Client()
		bucket = client.get_bucket(global_vars.USER_IMG_BUCKET)

		# path = str(user_id) + '/profile_picture.jpg'
		user_img = bucket.get_blob(path)
	else:
		user_img = None
	
	if user_img == None:
		user_img_media_link = None
		image_path = None
	else:
		user_img_media_link = user_img.media_link
		image_path = user_img.path



	data = {'user_id':str(user_id), 'first_name':first_name, 'last_name':last_name, 'phone_number':phone_number, 'email':email, 'image_path':image_path, 'image_media_link':user_img_media_link}

	resp = jsonify(data)
	resp.status_code = 200
	return resp




# Check if the given password satisfies our requirements
MIN_PASSWORD_SIZE = 8
def validate_password(password):
	if password is not None and len(password) < MIN_PASSWORD_SIZE:
		raise InvalidUsage('Password is too short.', status_code=400)

# Check if a user is already registered with the given email address
def validate_email(email):
	if email is not None:
		q = User.query(ndb.AND(User.email == email, User.status == 'Active'))
		u = q.get()
		if u is not None:
			raise InvalidUsage('Email address is already registered.', status_code=400)

# Check if a user is already registered with the given phone number
def validate_phone(phone_number):
	if phone_number is not None:
		q = User.query(ndb.AND(User.phone_number == phone_number, User.status == 'Active'))
		u = q.get()
		if u is not None:
			raise InvalidUsage('Phone number is already registered.', status_code=400)




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