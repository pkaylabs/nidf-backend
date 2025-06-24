from django.contrib.auth import login
from django.db.models import Q
from knox.models import AuthToken
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import OTP, User
from apis.serializers import (AddChurchSerializer, LoginSerializer, RegisterUserSerializer, ResetPasswordSerializer,
                              UserSerializer)
from nidfcore.utils.constants import UserType

import random


class LoginAPI(APIView):
    '''Login api endpoint'''
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
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
            "user": {**UserSerializer(user).data, "church_logo": user.get_church_logo()},
            "token": AuthToken.objects.create(user)[1],
        })


class VerifyOTPAPI(APIView):
    '''Verify OTP api endpoint'''
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        '''Use this endpoint to send OTP to the user'''
        phone = request.query_params.get('phone')
        if not phone:
            return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)
        code = random.randint(1000, 9999)
        try:
            existingotp = OTP.objects.filter(phone=phone).first()
            if existingotp:
                existingotp.delete()
            user = User.objects.filter(phone=phone).first()
            if not user:
                return Response({'error': 'User account not found'}, status=status.HTTP_404_NOT_FOUND)
            otp = OTP.objects.create(phone=phone, otp=code)
            otp.send_otp()
        except Exception as e:
            return Response({'error': 'Failed to send OTP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        otp = request.data.get('otp')
        phone = request.data.get('phone')
        user = User.objects.filter(phone=phone).first()
        if not user:
            return Response({'error': 'User account not found'}, status=status.HTTP_404_NOT_FOUND)
        if not phone:
            return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not otp:
            return Response({'error': 'Code is required'}, status=status.HTTP_400_BAD_REQUEST)
        otp = OTP.objects.filter(phone=phone, otp=otp).first()
        if not otp:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        if otp.is_expired():
            return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)
        otp.delete()
        user.phone_verified = True
        user.save()
        return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)


# class VerifyOTPAPI(APIView):
#     '''Verify OTP api endpoint'''
#     permission_classes = (permissions.IsAuthenticated,)

#     def get(self, request, *args, **kwargs):
#         '''Use this endpoint to send OTP to the user'''
#         user = request.user
#         phone = user.phone
#         code = random.randint(1000, 9999)
#         try:
#             OTP.objects.filter(phone=phone).delete()
#             otp = OTP.objects.create(phone=phone, otp=code)
#             otp.send_otp()
#         except Exception as e:
#             return Response({'error': 'Failed to send OTP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)

#     def post(self, request, *args, **kwargs):
#         user = request.user
#         phone = user.phone
#         otp = request.data.get('otp')
#         if not otp:
#             return Response({'error': 'OTP is required'}, status=status.HTTP_400_BAD_REQUEST)
#         otp = OTP.objects.filter(phone=phone, otp=otp).first()
#         if not otp:
#             return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
#         if otp.is_expired():
#             return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)
#         otp.delete()
#         user.phone_verified = True
#         user.save()
#         return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)

class RegisterAPI(APIView):
    '''Register api endpoint'''
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = RegisterUserSerializer(data=request.data)
        church_serializer = AddChurchSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            church_serializer.is_valid(raise_exception=True)
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
            church = church_serializer.save()
            user.church_profile = church
            user.save()
        login(request, user)
        return Response({
            "user": UserSerializer(user).data,
            "token": AuthToken.objects.create(user)[1],
        })
    
    
class LogoutAPI(APIView):
    '''Logout api endpoint'''
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
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
        if user.is_superuser or user.user_type == UserType.ADMIN.value or user.user_type == UserType.FINANCE_OFFICER.value:
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
            
            if user.is_superuser or user.user_type == UserType.ADMIN.value:
                # superusers and admins can create users
                print(serializer.validated_data)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            elif user.user_type == UserType.CHURCH_USER.value:
                # church users can only create users in their church
                serializer.save(church_profile=user.church_profile, user_type=UserType.CHURCH_USER.value)
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


class UserProfileAPIView(APIView):
    '''API endpoint to get and update user profile'''

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        '''Get user profile'''
        user = request.user
        serializer = UserSerializer(user)
        # inject the church logo
        serializer.data['church_logo'] = user.get_church_logo()
        print(serializer.data)
        return Response({**serializer.data, "church_logo": user.get_church_logo()}, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        '''Update user profile'''
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({**serializer.data, "church_logo": user.get_church_logo()}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ResetPasswordAPIView(APIView):
    '''API endpoint to reset user password'''

    permission_classes = (permissions.AllowAny,)
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        '''Reset user password'''
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            phone = serializer.data.get('phone')
            user = User.objects.filter(phone=phone).first()
            if not user:
                return Response({'phone': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)
            if not user.phone_verified:
                return Response({'phone': 'Phone not verified.'}, status=status.HTTP_400_BAD_REQUEST)
            if len(serializer.data.get('new_password')) < 1:
                return Response({'new_password': 'Password is too short.'}, status=status.HTTP_400_BAD_REQUEST)
            if not serializer.data.get('new_password') == serializer.data.get('confirm_password'):
                return Response({'new_password': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)