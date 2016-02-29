# Spartan_Server

### Project Organization
Each separate set of APIs are grouped into separate .py files based on objects. For example, all of the HTTP calls relating to users (creating new, updating info, etc)
are grouped into `users.py`. Similarly, all of the HTTP calls for listings (creating new, updating info, uploading pics) in the database are grouped into `listings.py`. 

To signal these functional distinctions in the methods, each file is given a special HTTP extension. For example, all API calls relating to users should be sent to `http://bygo-client-server.appspot.com/users/*` where `*` is the name of desired function. See the documentation in the Workflows section for more exmaples.



#################################################
#################################################
#################################################
############## TODO: FIX WORKFLOWS ##############
#################################################
#################################################
#################################################


appcfg.py -A molten-unison-112921 update app.yaml 
###################################################

########### USER FUNCTIONS ##############
### Create User
curl -H "Content-Type: application/json" -X POST -d "{\"first_name\":\"JJ\", \"last_name\":\"Qi\", \"email\":\"jj@bygo.io\", \"phone_number\":\"9876549878\", \"password\":\"\", \"signup_method\":\"Phone Number\", \"location_lat\":\"40.106361\", \"location_lon\":\"-88.2327326\"}" http://molten-unison-112921.appspot.com/user/create

### Deactivate User
curl -X DELETE http://molten-unison-112921.appspot.com/user/deactivate/user_id=5752571553644544

### Reactivate User
curl -H "Content-Type: application/json" -X POST -d {} http://molten-unison-112921.appspot.com/user/reactivate/user_id=5752571553644544

### Update User
curl -H "Content-Type: application/json" -X POST -d "{\"first_name\":\"Sayan\", \"last_name\":\"Roychowdhury\", \"email\":\"sayan@bygo.io\", \"phone_number\":\"7325704976\"}" http://molten-unison-112921.appspot.com/user/update/user_id=5752571553644544

### Add/Update User profile picture
curl -X POST -F "filename=profile_picture.jpg" -F "userfile=@C:/Users/Sayan/Desktop/10341994_10152165761279163_3623862560801127167_n.jpg" http://molten-unison-112921.appspot.com/user/new_user_image/user_id=5752571553644544

### Delete User Profile Picture
curl -X DELETE http://molten-unison-112921.appspot.com/user/delete_user_image/path=5752571553644544/profile_picture.jpg

### Get User Data (also returns a media link to their profile picture)
curl http://molten-unison-112921.appspot.com/user/get_info/user_id=5752571553644544

### Get User's Listings (user == owner)
curl http://molten-unison-112921.appspot.com/user/get_listings/user_id=5752571553644544

### Get User's Rented Listings (user == renter)
curl http://molten-unison-112921.appspot.com/user/get_rented_listings/user_id=5752571553644544



########### LISTING FUNCTIONS ##############
### Create Listing
curl -H "Content-Type: application/json" -X POST -d "{\"category_id\":\"5713573250596864\", \"name\":\"Garbage Headphones\", \"item_description\":\"This is a test desc.\", \"total_value\":\"75\", \"hourly_rate\":\"7.5\", \"daily_rate\":\"15\", \"weekly_rate\":\"30\"}" http://molten-unison-112921.appspot.com/listing/create/user_id=5752571553644544

### Delete Listing
curl -X DELETE http://molten-unison-112921.appspot.com/listing/delete/listing_id=5657382461898752

### Update Listing
curl -H "Content-Type: application/json" -X POST -d "{\"category_id\":\"5713573250596864\", \"name\":\"Knockoff Headphones\", \"item_description\":\"I AM A LIAR\", \"total_value\":\"75\", \"hourly_rate\":\"7.5\", \"daily_rate\":\"15\", \"weekly_rate\":\"30\", \"status\":\"Unlisted\"}" http://molten-unison-112921.appspot.com/listing/update/listing_id=5749563331706880

### Add listing image
curl -X POST -F "filename=belt.jpg" -F "userfile=@C:/Users/Sayan/Desktop/8-4-10-logitech60037.jpg" http://molten-unison-112921.appspot.com/listing/new_listing_image/listing_id=5657382461898752

### Delete listing image
curl -X DELETE http://molten-unison-112921.appspot.com/listing/delete_listing_image/path=5682617542246400/40mmOLChntSglLp2686GovBlkSnp-2.jpg

### Get a listing's data
curl http://molten-unison-112921.appspot.com/listing/get_info/listing_id=5657382461898752