from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apis.models import ProgressReport
from apis.serializers import AddProgressReportSerializer, GetProgressReportSerializer
from nidfcore.utils.constants import ApplicationStatus, UserType
from nidfcore.utils.permissions import IsCentralAndSuperUser


class ProgressReportsAPIView(APIView):
    '''Progress Reports API view'''

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        '''Get all progress reports'''
        user = request.user

        if user.is_superuser or user.user_type == UserType.ADMIN.value:
            # superuser and admin can view all progress reports
            progress_reports = ProgressReport.objects.all().order_by('-created_at')
            serializer = GetProgressReportSerializer(progress_reports, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif user.user_type == UserType.CHURCH_USER.value:
            # church users can only see progress reports belonging to their church
            progress_reports = ProgressReport.objects.filter(application__church=user.church_profile).order_by('-created_at')
            serializer = GetProgressReportSerializer(progress_reports, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # anyone else shouldn't see any progress reports
            progress_reports = ProgressReport.objects.none()
            serializer = GetProgressReportSerializer(progress_reports, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
    def post(self, request, *args, **kwargs):
        '''Create a new progress report'''
        serializer = AddProgressReportSerializer(data=request.data)
        if serializer.is_valid():
            application = serializer.validated_data.get('application')
            if application.church != request.user.church_profile:
                return Response(
                    {
                        "message": "You are not allowed to create a progress report for this application"
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            progress_report = serializer.save(created_by=request.user)
            return Response(GetProgressReportSerializer(progress_report).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class VerifyProgressReportAPIView(APIView):
    '''Endpoint to verify progress reports'''

    permission_classes = [IsCentralAndSuperUser]

    def post(self, request, *args, **kwargs):
        user = request.user

        if not (user.is_superuser or user.user_type == UserType.ADMIN.value):
            # deny access to anyone not superuser or admin user
            return Response({"message": "You are not allowed to verify progress report"}, status=status.HTTP_401_UNAUTHORIZED)
        
        report_id = request.data.get('reportid')
        report = ProgressReport.objects.filter(report_id=report_id).first()

        if report == None:
            return Response({"message": "Report not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # change the status to verified
        report.status = ApplicationStatus.VERIFIED.value
        report.updated_by = user
        report.save()

        return Response({"message": "Progress Report Verified Successfully"}, status=status.HTTP_200_OK)