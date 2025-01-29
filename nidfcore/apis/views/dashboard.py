from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apis.models import Application
from nidfcore.utils.constants import ApplicationStatus, UserType


class DashboardAPIView(APIView):
    '''Dashboard API View'''
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        '''GET request'''
        user = request.user
        if user.is_superuser or user.user_type == UserType.ADMIN.value or user.user_type == UserType.FINANCE_OFFICER.value:
            return Response({
                'total_pending': Application.objects.filter(status=ApplicationStatus.PENDING.value).count(),
                'total_approved': Application.objects.filter(status=ApplicationStatus.APPROVED.value).count(),
                'total_rejected': Application.objects.filter(status=ApplicationStatus.REJECTED.value).count(),
                'total_disbursed': sum([app.get_disbursed_amount() for app in Application.objects.all()]),
                'total_repaid': sum([app.get_repayment_amount() for app in Application.objects.all()]),
                'outstanding_balance': sum([app.get_disbursed_amount() for app in Application.objects.all()]) - sum([app.get_repayment_amount() for app in Application.objects.all()]),
            }, status=status.HTTP_200_OK)
        elif user.user_type == UserType.CHURCH_USER.value and user.church_profile != None:
            church = user.church_profile
            return Response({
                'amount_received': church.get_amount_received(),
                'amount_repaid': church.get_amount_repaid(),
                'repayment_percentage': church.get_repaid_percentage(),
                'next_due_date': church.get_next_due_date(),
            }, status=status.HTTP_200_OK)
        else:
            return Response({"message": "User does not have a church profile"}, status=status.HTTP_400_BAD_REQUEST)