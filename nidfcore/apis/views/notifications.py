from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.utils import timezone

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
            notification = Notification.objects.filter(id=notification_id).first()

        if user.user_type == UserType.CHURCH_USER.value:
            return Response({"message": "You are not allowed to create notifications"}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = NotificationSerializer(notification, data=request.data)
        if serializer.is_valid():
            if notification:
                notif = serializer.save(updated_by=user)
                # Send notification to the targeted users if the notification is not scheduled
                if not notif.is_scheduled:
                    notif.broadcast(user=user)
                return Response({"message": "Notification Updated Successfully" ,"data":serializer.data}, status=status.HTTP_200_OK)
            else:
                notif = serializer.save(created_by=user)
                # Send notification to the targeted users if the notification is not scheduled
                if not notif.is_scheduled:
                    notif.broadcast(user=user)
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
        

class ScheduledNotificationBroadcastAPIView(APIView):
    '''handles the scheduled notifications'''
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        # get notifications that are scheduled to be sent today
        notifications = Notification.objects.filter(is_scheduled=True)
        for notification in notifications:
            if not notification.can_broadcast():
                print(f"Skipping notification {notification.id} as it is not ready to be broadcasted")
                continue
            # send the notification to the targeted users
            print(f"Broadcasting notification {notification.id} to {notification.target} users")
            notification.broadcast(user=None)
            print("============================================")
        return Response({"message": "Request Submitted Successfully"}, status=status.HTTP_200_OK)
