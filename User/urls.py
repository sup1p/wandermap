from django.urls import path
from User import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),

    path('trips/', views.trip_create_getlist, name='trip_create_getlist'),  #post-create, get-list of trips
    path('trips/<int:trip_id>/', views.trip_get_edit_delete, name='trip_get_edit_delete'), #patch-edit delete-delete get-trip ONE EXACT
    path('trips/<int:trip_id>/upload_photo/', views.upload_trip_photo, name='trip_upload_photo'),#post-upload up to 5 photo
    path('trips/<int:photo_id>/delete_photo/', views.delete_trip_photo, name='trip_delete_photo'),#delete by id

    path('profile/sharelink/', views.share_link_get, name='share_link_get'),#get private and public link - must provide email
    path('profile/sharepublic/<str:email>/', views.share_public_profile, name='share_public_profile'),#get someone's all trips by email
    path('profile/shareprivate/<str:private_share_token>/', views.share_private_profile, name='share_private_profile'),#get someone's all trips by sharetoken
    path('profile/changepublicity/', views.change_publicity, name='change_publicity'), #PATCH change users publicicity(private/public)

    path('autocomplete/', views.autocomplete, name='autocomplete'),#send "q=smt" in query params, to get suggestions
    path('autocomplete/lat_long/',views.autocomplete_lat_long, name='autocomplete_lat_long'),
]