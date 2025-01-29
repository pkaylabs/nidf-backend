from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apis.models import Repayment
from apis.serializers import AddRepaymentSerializer, GetRepaymentSerializer
from nidfcore.utils.constants import UserType


class RepaymensAPIView(APIView):
    '''Repayments API view'''
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        '''Get all repayments'''
        # superuser, admin and finance officer can view all repayments
        user = request.user
        if user.is_superuser or user.user_type == UserType.ADMIN.value or user.user_type == UserType.FINANCE_OFFICER.value:
            repayments = Repayment.objects.all().order_by('-date_paid')
            serializer = GetRepaymentSerializer(repayments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif user.user_type == UserType.CHURCH_USER.value:
            # church users can only see repayments belonging to their church
            repayments = Repayment.objects.filter(application__church=user.church_profile).order_by('-date_paid', '-created_at')
            serializer = GetRepaymentSerializer(repayments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            repayments = Repayment.objects.none()
            serializer = GetRepaymentSerializer(repayments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request, *args, **kwargs):
        '''Create a new repayment'''
        serializer = AddRepaymentSerializer(data=request.data)
        if serializer.is_valid():
            application = serializer.validated_data.get('application')
            if application.church != request.user.church_profile:
                return Response(
                    {
                        "message": "You are not allowed to create a repayment for this application"
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            repayment = serializer.save(created_by=request.user)
            return Response(GetRepaymentSerializer(repayment).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)