from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apis.models import Repayment
from apis.serializers import AddRepaymentSerializer, GetRepaymentSerializer
from nidfcore.utils.constants import ApplicationStatus, UserType
from nidfcore.utils.permissions import IsCentralAndSuperUser


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
    

    def put(self, request, *args, **kwargs):
        '''update a repayment: can only update an unprocessed repayment'''
        user = request.user
        repayment_id = request.data.get('repayment')
        if not repayment_id:
            return Response({"message": "Repayment ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        # only the church user can update a repayment
        if user.user_type == UserType.CHURCH_USER.value:
            repayment = Repayment.objects.filter(repayment_id=repayment_id, application__church=user.church_profile).first()
            if repayment:
                if repayment.status == ApplicationStatus.PENDING.value:
                    serializer = AddRepaymentSerializer(repayment, data=request.data, partial=True)
                    if serializer.is_valid():
                        repayment = serializer.save(updated_by=user)
                        return Response(GetRepaymentSerializer(repayment).data, status=status.HTTP_200_OK)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                return Response({"message": "Processed Repayment cannot be updated"}, status=status.HTTP_403_FORBIDDEN)
            return Response({"message": "Repayment record not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "You are not allowed to update repayment"}, status=status.HTTP_403_FORBIDDEN)

    
    def delete(self, request, *args, **kwargs):
        '''Delete a repayment'''
        user = request.user
        repayment_id = request.data.get('repayment')
        if not repayment_id:
            return Response({"message": "Repayment ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        # only the finance officer and church user can delete a repayment
        if user.user_type == UserType.FINANCE_OFFICER.value or user.user_type == UserType.CHURCH_USER.value:
            if user.user_type == UserType.CHURCH_USER.value:
                repayment = Repayment.objects.filter(repayment_id=repayment_id, application__church=user.church_profile).first()
            else:
                repayment = Repayment.objects.filter(repayment_id=repayment_id).first()
            if repayment:
                if repayment.status == ApplicationStatus.PENDING.value:
                    repayment.delete()
                    return Response({"message": "Repayment deleted successfully"}, status=status.HTTP_200_OK)
                return Response({"message": "Processed Repayment cannot be deleted"}, status=status.HTTP_403_FORBIDDEN)
            return Response({"message": "Repayment record not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message": "You are not allowed to delete a repayment"}, status=status.HTTP_403_FORBIDDEN)
            

class VerifyRepaymentAPIView(APIView):
    '''Endpoint to verify repayments'''

    permission_classes = [IsCentralAndSuperUser]

    def post(self, request, *args, **kwargs):
        user = request.user

        if not (user.user_type == UserType.FINANCE_OFFICER.value):
            # only finance office can verify repayments
            return Response({"message": "You are not allowed to verify repayment"}, status=status.HTTP_401_UNAUTHORIZED)
        
        repayment_id = request.data.get('repaymentid')
        repayment_status = request.data.get('status')
        repayment = Repayment.objects.filter(repayment_id=repayment_id).first()

        if repayment == None:
            return Response({"message": "Repayment record not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if repayment_status.upper() not in [ApplicationStatus.APPROVED.value, ApplicationStatus.REJECTED.value]:
            return Response({"message": "Status not acceptable"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        # change the status...
        if repayment_status.upper() in [ApplicationStatus.APPROVED.value]:
            repayment.status = ApplicationStatus.APPROVED.value
            msg = "Repayment Record Verified Successfully"
        else:
            repayment.status = ApplicationStatus.REJECTED.value
            msg = "Repayment Record Rejected Successfully"
        repayment.updated_by = user
        repayment.save()

        return Response({"message": msg}, status=status.HTTP_200_OK)