import uuid
import requests
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import Token, RefreshToken
from rest_framework.parsers import MultiPartParser

from NfacMapBox import settings
from User.models import CustomUser, Trip, TripPhoto, CustomUserProfile
from User.serializers import UserRegistrationSerializer, TripsSerializer, CustomUserProfileSerializer



@api_view(['POST'])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user=user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        }, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user = CustomUser.objects.get(email=email)
        print("user.email:", user.email)
        print("user.password:", user.password)
        print("request email:", email)
        if not user.check_password(password):
            return Response({'message':'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    except CustomUser.DoesNotExist:
        return Response({'message':'Invalid credentials'}, status=status.HTTP_404_NOT_FOUND)

    refresh = RefreshToken.for_user(user=user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
    }, status=status.HTTP_200_OK)

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def trip_create_getlist(request):
    if request.method == 'POST':    #create new trip
        serializer = TripsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':   #all trips list
        user = request.user
        trips = Trip.objects.filter(user=user)
        all_data = []
        for trip in trips:
            serializer = TripsSerializer(trip)
            trip_data = serializer.data
            photos = trip.photos.values('id', 'image_url')
            trip_data['photo_urls'] = [{'id': thing['id'], 'url': thing['image_url']} for thing in photos]
            all_data.append(trip_data)
        response_data = {'trips': all_data}
        return Response(response_data, status=status.HTTP_200_OK)

@api_view(['DELETE','GET','PATCH'])
@permission_classes([IsAuthenticated])
def trip_get_edit_delete(request,trip_id):
    try:
        trip = Trip.objects.get(id=trip_id)
    except Trip.DoesNotExist:
        return Response({'message':'Trip not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':  # get one exact trip
        serializer = TripsSerializer(trip)
        data = serializer.data
        photos = trip.photos.values('id', 'image_url')
        data['photo_urls'] = [{'id': thing['id'], 'url': thing['image_url']} for thing in photos]
        return Response(data, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':    # delete exact trip
        if trip.user.id == request.user.id:
            trip.delete()
            return Response({'message':'Trip deleted'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'message':"You cannot delete someone else's trip"}, status=status.HTTP_401_UNAUTHORIZED)
    elif request.method == 'PATCH':     # edit exact trip
        if trip.user.id == request.user.id:
            serializer = TripsSerializer(trip, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message':"You cannot edit someone else's trip"}, status=status.HTTP_401_UNAUTHORIZED)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def share_link_get(request):
    user_profile = CustomUserProfile.objects.get(user=request.user)
    user=user_profile.user
    email=str(user.email)
    public_link = str(email)

    if (not user_profile.private_share_token
        or user_profile.private_token_expires_at < timezone.now()
        or user_profile.private_share_token is None):
        user_profile.generate_private_token()
    private_link = str(user_profile.private_share_token)

    return Response({"public": {"enabled": user_profile.is_public,"path":public_link,
                        },"private": {"path":private_link,"expires_at":user_profile.private_token_expires_at}}, status=status.HTTP_200_OK)
@api_view(['GET'])
def share_public_profile(request, email):
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response({'message':'Not found by this email'}, status=status.HTTP_404_NOT_FOUND)
    if user.profile.is_public is False:
        return Response({'message':'Account is not public'}, status=status.HTTP_403_FORBIDDEN)

    trips = Trip.objects.filter(user=user)
    all_data = []
    for trip in trips:
        serializer = TripsSerializer(trip)
        trip_data = serializer.data
        photos = trip.photos.values('id', 'image_url')
        trip_data['photo_urls'] = [{'id': thing['id'], 'url': thing['image_url']} for thing in photos]
        all_data.append(trip_data)
    response_data = {'trips': all_data, 'username': user.username}
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def share_private_profile(request, private_share_token):
    try:
        user_profile = CustomUserProfile.objects.get(private_share_token=private_share_token)
    except CustomUserProfile.DoesNotExist:
        return Response({'message':'User not found'}, status=status.HTTP_404_NOT_FOUND)
    if user_profile.private_token_expires_at < timezone.now():
        return Response({'message':'Token is expired'}, status=status.HTTP_403_FORBIDDEN)
    user = user_profile.user
    trips = Trip.objects.filter(user=user)
    all_data = []
    for trip in trips:
        serializer = TripsSerializer(trip)
        trip_data = serializer.data
        photos = trip.photos.values('id', 'image_url')
        trip_data['photo_urls'] = [{'id': thing['id'], 'url': thing['image_url']} for thing in photos]
        all_data.append(trip_data)
    response_data = {'trips': all_data, 'username': user.username}
    return Response(response_data, status=status.HTTP_200_OK)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def change_publicity(request):
    try:
        user_profile = CustomUserProfile.objects.get(user=request.user)
    except CustomUserProfile.DoesNotExist:
        return Response({'message':'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = CustomUserProfileSerializer(user_profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def upload_trip_photo(request, trip_id):
    try:
        trip = Trip.objects.get(id=trip_id, user=request.user)
    except Trip.DoesNotExist:
        return Response({"message":'trip not found, either user or id is wrong'}, status=status.HTTP_404_NOT_FOUND)
    photos = request.FILES.getlist('photos')
    if len(photos) > 5:
        return Response({'message':'Too many photos, max is 5 per one request'}, status=status.HTTP_400_BAD_REQUEST)
    uploaded=[]
    for file in photos:
        extension = file.name.split('.')[-1].lower()
        filename=f"{uuid.uuid4()}.{extension}"
        path = f"trip_photos/{filename}"

        content_type = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'webp': 'image/webp'
        }.get(extension, 'application/octet-stream')
        SUPABASE_URL=settings.SUPABASE_URL.rstrip('/')
        bucket=settings.BUCKET_NAME
        service_key=settings.SERVICE_ROLE_KEY
        url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{path}"
        print(url)

        headers = {
            "Authorization": f"Bearer {service_key}",
            "Content-Type": content_type,
            "x-upsert": "true"
        }
        file.seek(0)
        print("Uploading:", url)
        print("Content-Type:", content_type)
        print("Size:")
        response = requests.put(url, headers=headers, data=file.read())
        if response.status_code == 200:
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}"
            TripPhoto.objects.create(trip=trip, image_url=public_url)
            uploaded.append(public_url)
        else:
            return Response({'error': f"Upload failed for {file.name}: {response.status_code}"}, status=500)
    return Response({'uploaded': uploaded}, status=status.HTTP_201_CREATED)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_trip_photo(request, photo_id):
    try:
        photo = TripPhoto.objects.get(id=photo_id, trip__user=request.user)
    except TripPhoto.DoesNotExist:
        return Response({'message':'Trip photo not found, either id or user is wrong'}, status=status.HTTP_404_NOT_FOUND)
    url = photo.image_url
    bucket = settings.BUCKET_NAME
    base_url=f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/public/{bucket}/"
    if not url.startswith(base_url):
        return Response({"message":"invalid image url"}, status=status.HTTP_400_BAD_REQUEST)
    object_path=url.replace(base_url,"")
    delete_url=f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/{bucket}/{object_path}"
    headers={
        "Authorization": f"Bearer {settings.SERVICE_ROLE_KEY}",
    }
    response = requests.delete(delete_url, headers=headers)
    if response.status_code not in [200,204]:
        return Response({'error': "Delete failed"}, status=response.status_code)
    photo.delete()
    return Response({'message':'Trip photo deleted'}, status=status.HTTP_204_NO_CONTENT)
@api_view(['GET'])
def autocomplete(request):
    query = request.GET.get('q')
    if not query or query is None:
        return Response([])
    nominatim_url="https://nominatim.openstreetmap.org/search"
    params={"q": query, "format": "json","addressdetails": 1,"limit":5}
    headers={"User-Agent":"NfacMapBox/1.0"}
    response = requests.get(nominatim_url, params=params, headers=headers)
    results = response.json()
    suggestions = []
    for result in results:
        address=result.get("display_name","")
        lat=result.get("lat",None)
        lon=result.get("lon",None)
        suggestions.append({"label":address,"lat":lat,"lon":lon})
    return Response(suggestions)

