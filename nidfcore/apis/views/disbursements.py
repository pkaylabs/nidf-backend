from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apis.models import Disbursement
from apis.serializers import (AddDisbursementSerializer,
                              GetDisbursementSerializer)
from nidfcore.utils.constants import UserType


class DisbursementsAPIView(APIView):
    '''Disbursements API view'''
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        '''Handles GET requests'''
        user = request.user
        if user.is_superuser or user.user_type == UserType.ADMIN.value or user.user_type == UserType.FINANCE_OFFICER.value:
            # superuser, admin and finance officer can view all disbursements
            disbursements = Disbursement.objects.all().order_by('-created_at')
            serializer = GetDisbursementSerializer(disbursements, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif user.user_type == UserType.CHURCH_USER.value:
            # church users can only see disbursements belonging to their church
            disbursements = Disbursement.objects.filter(application__church=user.church_profile).order_by('-created_at')
            serializer = GetDisbursementSerializer(disbursements, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # anyone else shouldn't see any disbursements
            disbursements = Disbursement.objects.none()
            serializer = GetDisbursementSerializer(disbursements, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
    def post(self, request, *args, **kwargs):
        '''Handles POST requests'''
        user = request.user
        if user.user_type != UserType.FINANCE_OFFICER.value:
            # only finance officers can create disbursements
            return Response(
                {
                    "message": "You are not allowed to create a disbursement"
                },
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = AddDisbursementSerializer(data=request.data)
        if serializer.is_valid():
            disbursement = serializer.save(created_by=request.user)
            return Response(GetDisbursementSerializer(disbursement).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
