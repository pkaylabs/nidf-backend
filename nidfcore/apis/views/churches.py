from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Church
from apis.serializers import AddChurchSerializer, GetChurchSerializer
from nidfcore.utils.constants import UserType


class ChurchProfileAPIView(APIView):
    '''API endpoint for church profile'''
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        '''Returns the church profile of the authenticated user'''
        user = request.user
        if user.church_profile:
            serializer = GetChurchSerializer(user.church_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'Church profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, *args, **kwargs):
        '''Updates the church profile of the authenticated user'''
        user = request.user
        if user.church_profile:
            serializer = AddChurchSerializer(user.church_profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Church profile not found'}, status=status.HTTP_404_NOT_FOUND)


class ChurchesAPIView(APIView):
    '''API endpoint for churches'''
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        '''Returns a list of churches'''
        # everyone can view the list of churches
        churches = Church.objects.all().order_by('location_name')
        serializer = GetChurchSerializer(churches, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request, *args, **kwargs):
        '''Adds a new church'''
        user = request.user
        otp_verified = user.phone_verified
        if user.is_superuser and user.user_type == UserType.ADMIN.value:
            # Admins can create a church for a church user
            serializer = AddChurchSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif user.user_type == UserType.CHURCH_USER.value and user.church_profile:
            # Church users can only create a church if they don't have one
            return Response({'error': 'Church Already Exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        elif user.user_type == UserType.CHURCH_USER.value and not otp_verified:
            # Church users can only create a church if their phone is verified
            return Response({'error': 'Phone not verified'}, status=status.HTTP_400_BAD_REQUEST)
        
        elif user.user_type == UserType.CHURCH_USER.value and not user.church_profile:
            serializer = AddChurchSerializer(data=request.data)
            if serializer.is_valid():
                church = serializer.save(created_by=user)
                user.church_profile = church
                user.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # Unauthorized
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)