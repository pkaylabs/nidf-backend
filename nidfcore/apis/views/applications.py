from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apis.models import Application
from apis.serializers import AddApplicationSerializers, ApplicationSerializers
from nidfcore.utils.constants import ApplicationStatus, ConstLists, UserType
from nidfcore.utils.permissions import IsCentralAndSuperUser
from nidfcore.utils.services import send_sms


class ApplicationsAPIView(APIView):
    '''API Endpoints for applications'''

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user

        # superuser, admin users and finance officers can view all applications
        if user.is_superuser or user.user_type == UserType.ADMIN.value or user.user_type == UserType.FINANCE_OFFICER.value:
            applications = Application.objects.all().order_by('-created_at')
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
            serializer = AddApplicationSerializers(application, data=request.data)
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
        serializer = AddApplicationSerializers(data=request.data)

        if serializer.is_valid():
            church = serializer.validated_data.get('church') or user.church_profile
            application = serializer.save(created_by=user, updated_by=user, church=church)
            # notify the church user that an application has been created
            application.notify_applicant(started=True)
            return Response(
                {
                    "message": "Application Created Successfully",
                    "application": ApplicationSerializers(application).data
                }, status=status.HTTP_201_CREATED)

        # there was an error in the data
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, *args, **kwargs):
        '''uses put method to mark application as submitted (pending review).'''
        user = request.user
        applicationid = request.data.get('application')

        if user.is_superuser or user.user_type == UserType.ADMIN.value:
            # admins can submit any application
            application = Application.objects.filter(application_id=applicationid).first()
        else:
            # church users can only submit applications belonging to their church
            application = Application.objects.filter(church=user.church_profile, application_id=applicationid).first()

        if application == None:
            return Response({"message": "Application not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            application.status = ApplicationStatus.PENDING.value
            application.updated_by = user
            application.save()
            # notify the church that an application has been submitted
            application.notify_applicant(submitted=True)
            return Response({"message": "Application Submitted Successfully"}, status=status.HTTP_200_OK)
        

    def delete(self, request, *args, **kwargs):
        '''delete an application'''
        # NOTE: PREVENT DELETION OF APPLICATIONS WITH DISBURSEMENTS
        user = request.user
        applicationid = request.data.get('application')

        if user.is_superuser or user.user_type == UserType.ADMIN.value or user.user_type == UserType.FINANCE_OFFICER.value:
            # admins can delete any application
            application = Application.objects.filter(application_id=applicationid).first()
        else:
            # church users can only delete applications belonging to their church
            application = Application.objects.filter(church=user.church_profile, application_id=applicationid).first()

        if application == None:
            return Response({"message": "Application not found"}, status=status.HTTP_404_NOT_FOUND)
        if application.status != ApplicationStatus.DRAFT.value:
            return Response({"message": "Cannot delete a submitted application"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            application.delete()
            return Response({"message": "Application Deleted Successfully"}, status=status.HTTP_200_OK)


class ProcessApplicationsAPIView(APIView):
    '''enpoint to process applications: approve, reject'''

    permission_classes =( IsCentralAndSuperUser,)

    def post(self, request, *args, **kwargs):
        user = request.user
        is_superuser = user.is_superuser
        is_finance_officer = user.user_type == UserType.FINANCE_OFFICER.value
        is_admin_user = user.user_type == UserType.ADMIN.value

        if not (is_superuser or is_admin_user or is_finance_officer):
            # deny access to any user not in the ADMIN category
            return Response({"message": "You are not allowed to process application"},  status=status.HTTP_401_UNAUTHORIZED)
        else:
            application_status = request.data.get('status')
            application_id = request.data.get('application')

            application = Application.objects.filter(application_id=application_id).first()
            if application == None:
                return Response({"message": "Application not found"},  status=status.HTTP_404_NOT_FOUND)
            
            application_statuses = [i[0] for i in ConstLists.application_statuses]
            if application_status.strip().upper() in application_statuses:
                previous_status = application.status
                application.status = application_status.upper()
                application.updated_by = user
                application.save()
                # notify the church that an application has been processed
                if application_status == ApplicationStatus.APPROVED.value:
                    try:
                        application.set_award_reference()
                        application.save()
                    except Exception as e:
                        # if there is an error setting the award reference, return an error response
                        application.status = previous_status  # revert to previous status
                        application.save()
                        return Response({"message": "Error setting award reference: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    application.notify_applicant(approved=True)
                elif application_status == ApplicationStatus.REJECTED.value:
                    application.notify_applicant(rejected=True)

                return Response({"message": "Application Status Changed"},  status=status.HTTP_200_OK)
            else:
                return Response({"message": "Status is not acceptable"},  status=status.HTTP_406_NOT_ACCEPTABLE)
            

class AdditionalInformationAPIView(APIView):
    '''endpoint to request for additional information from applicants'''

    permission_classes =( IsCentralAndSuperUser,)

    def post(self, request, *args, **kwargs):
        user = request.user
        is_superuser = user.is_superuser
        is_finance_officer = user.user_type == UserType.FINANCE_OFFICER.value
        is_admin_user = user.user_type == UserType.ADMIN.value

        if not (is_superuser or is_admin_user or is_finance_officer):
            # deny access to any user not in the ADMIN category
            return Response({"message": "You are not allowed to perform this action"},  status=status.HTTP_401_UNAUTHORIZED)
        
        message = request.data.get('message')
        application_id = request.data.get('application')

        application = Application.objects.filter(application_id=application_id).first()
        if application == None:
            return Response({"message": "Application not found"},  status=status.HTTP_404_NOT_FOUND)
        
        if message.strip() == '' or message == None:
            return Response({"message": "Message is required"},  status=status.HTTP_404_NOT_FOUND)
        
        phones = [application.church.pastor_phone, application.church.church_phone]

        # format the message
        title = "NIDF Request for Info."
        msg = title + "\n" + message

        # send sms to user
        send_sms(message=msg, recipients=phones)

        # change the status back to draft
        application.status = ApplicationStatus.DRAFT.value
        application.updated_by = user
        application.save()

        return Response({"message": "Request Sent Successfully"},  status=status.HTTP_200_OK)