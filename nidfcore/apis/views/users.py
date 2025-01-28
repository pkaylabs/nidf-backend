from django.contrib.auth import login
from knox.models import AuthToken
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apis.serializers import LoginSerializer, RegisterUserSerializer, UserSerializer

class LoginAPI(APIView):
    '''Login api endpoint'''
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
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
        request.user.auth_token.delete()
        return Response({"status": "success"}, status=status.HTTP_200_OK)