from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Church
from apis.models import Application
from apis.serializers import ApplicationSerializers
from nidfcore.utils.constants import UserType


class ApplicationsAPIView(APIView):
    '''API Endpoints for applications'''

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user

        # superuser, admin users and finance officers can view all applications
        if user.is_superuser or user.user_type == UserType.ADMIN.value or user.user_type == UserType.FINANCE_OFFICER.value:
            applications = Application.objects.all().order_by('-created_by')
            serializer = ApplicationSerializers(applications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif user.user_type == UserType.CHURCH_USER.value:
            # church users can only see applications belonging to their church
            applications = Application.objects.filter(church=user.church_profile).order_by('-created_at')
            serializer = ApplicationSerializers(applications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # anyone else shouldn't see any applications
            applications = Application.objects.none()
            serializer = ApplicationSerializers(applications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        '''POST request to create or update an application'''
        user = request.user

        application_id = request.data.get('application_id')

        if application_id and Application.objects.filter(application_id=application_id).exists():
            print('Application exists already...')
            # application exists: update the application
            application = Application.objects.get(application_id=application_id)
            serializer = ApplicationSerializers(application, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(updated_by=user)
            return Response(
                {
                    "message": "Application Updated Successfully",
                    "application": serializer.data
                },
                status=status.HTTP_200_OK
            )

        # Create a new application
        print('Creating a new application...')
        serializer = ApplicationSerializers(data=request.data)

        if serializer.is_valid():
            church = serializer.validated_data.get('church') or user.church_profile
            serializer.save(created_by=user, updated_by=user, church=church)
            return Response(
                {
                    "message": "Application Created Successfully",
                    "application": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        # there was an error in the data
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
