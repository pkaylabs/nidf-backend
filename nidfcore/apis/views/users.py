from django.contrib.auth import login
from django.db.models import Q
from knox.models import AuthToken
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from apis.serializers import LoginSerializer, RegisterUserSerializer, UserSerializer
from nidfcore.utils.constants import UserType

class LoginAPI(APIView):
    '''Login api endpoint'''
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            print(e)
            for field in list(e.detail):
                error_message = e.detail.get(field)[0]
                field = f"{field}: " if field != "non_field_errors" else ""
                response_data = {
                    "status": "error",
                    "error_message": f"{field} {error_message}",
                    "user": None,
                    "token": None,
                }
                return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user = serializer.validated_data
       
        login(request, user)

        # Delete existing token
        AuthToken.objects.filter(user=user).delete()
        return Response({
            "user": UserSerializer(user).data,
            "token": AuthToken.objects.create(user)[1],
        })

class RegisterAPI(APIView):
    '''Register api endpoint'''
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = RegisterUserSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            for field in list(e.detail):
                error_message = e.detail.get(field)[0]
                field = f"{field}: " if field != "non_field_errors" else ""
                response_data = {
                    "status": "error",
                    "error_message": f"{field} {error_message}",
                    "user": None,
                    "token": None,
                }
                return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user = serializer.save()
        login(request, user)
        return Response({
            "user": UserSerializer(user).data,
            "token": AuthToken.objects.create(user)[1],
        })
    
class LogoutAPI(APIView):
    '''Logout api endpoint'''
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        user = request.user
        AuthToken.objects.filter(user=user).delete()
        return Response({"status": "success"}, status=status.HTTP_200_OK)
    

class UsersAPIView(APIView):
    '''API endpoint to get and create update and delete users'''

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        '''
        Get all users: superusers get all users, 
        church users get only users in their church, 
        other users get only themselves
        '''
        user = request.user
        if user.is_superuser or user.user_type == UserType.ADMIN.value:
            # superusers and admins get all users
            users = User.objects.all().order_by('-created_at', 'name')
        elif user.user_type == UserType.CHURCH_USER.value:
            # church users get only users in their church
            users = User.objects.filter(church_profile=user.church_profile, deleted=False).order_by('-created_at', 'name')
        else:
            # other users get only themselves
            users = User.objects.filter(id=user.id)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def post(self, request):
        '''POST request to create a new user'''
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            # check if the user with same phone or email already exists
            existing_email = User.objects.filter(email=serializer.validated_data.get('email'))
            existing_phone = User.objects.filter(email=serializer.validated_data.get('phone'))
            if existing_email.exists():
                return Response({'error': 'User with the same email already exists'}, status=status.HTTP_400_BAD_REQUEST)
            if existing_phone.exists():
                return Response({'error': 'User with the same phone already exists'}, status=status.HTTP_400_BAD_REQUEST)
            user = request.user
            if user.user_type == UserType.CHURCH_USER.value:
                # church users can only create users in their church
                serializer.save(church_profile=user.church_profile, user_type=UserType.CHURCH_USER.value)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            elif user.is_superuser or user.user_type == UserType.ADMIN.value:
                # superusers and admins can create users
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'You are not allowed to create users'}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        '''Delete a user'''
        request_user = request.user
        user_id = request.data.get('userid')
        if request_user.is_superuser or request_user.user_type == UserType.ADMIN.value:
            # superusers and admins can delete users who are not superusers
            user = User.objects.filter(id=user_id, is_superuser=False, deleted=False).first()
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            user.deleted = True
            user.save()
            return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        
        elif user.user_type == UserType.CHURCH_USER.value:
            # church users can only delete users in their church
            user = User.objects.filter(id=user_id, church_profile=user.church_profile, deleted=False).first()
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            user.deleted = True
            user.save()
            return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'You are not allowed to delete users'}, status=status.HTTP_403_FORBIDDEN)


    
