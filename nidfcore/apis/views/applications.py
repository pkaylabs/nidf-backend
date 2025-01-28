from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

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
