from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from apis.models import Notification
from apis.serializers import NotificationSerializer
from nidfcore.utils.constants import Target, UserType


class NotificationsAPIView(APIView):
    """
    API view to retrieve notifications for a user.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Retrieve notifications for the authenticated user.
        """
        user = request.user
        # church users can only see notifications targeted to their church
        if user.user_type == UserType.CHURCH_USER.value:
            notifications = Notification.objects.filter(
                Q(traget=Target.ALL.value) | Q(target=Target.CHURCH.value)
            ).order_by('-created_at')
        # admin users can see all notifications
        notifications = Notification.objects.all().order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        '''Post a new notification'''
        user = request.user
        notification_id = request.data.get('notification')
        notification = None
        if notification_id:
            notification = Notification.objects.get(id=notification_id)

        if user.user_type == UserType.CHURCH_USER.value:
            return Response({"message": "You are not allowed to create notifications"}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = NotificationSerializer(notification, data=request.data, partial=True)
        if serializer.is_valid():
            if notification:
                serializer.save(updated_by=user)
                return Response({"message": "Notification Updated Successfully" ,"data":serializer.data}, status=status.HTTP_200_OK)
            else:
                serializer.save(created_by=user)
            return Response({"message": "Notification Created Successfully" ,"data":serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        '''Delete a notification'''
        user = request.user
        if user.user_type == UserType.CHURCH_USER.value:
            return Response({"message": "You are not allowed to delete notifications"}, status=status.HTTP_401_UNAUTHORIZED)
        notification_id = request.data.get('notification')
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.delete()
            return Response({"message": "Notification deleted successfully"}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({"message": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)