from django.contrib.auth import authenticate
from rest_framework import serializers
from django.db.models import Q

from accounts.models import Church, District, Region, User
from apis.models import Application, Disbursement, Notification, ProgressReport, Repayment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', 'groups', 'user_permissions']


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        '''login credentials can be email or phone'''
        user = authenticate(**data) # default credential check - email and password
        if user and user.is_active and ((hasattr(user, "deleted") and user.deleted == False) or not hasattr(user, "deleted")):
            return user
        if not user:
            # Try to authenticate with phone if email fails
            phone_or_email = data.get('email')
            check_user = User.objects.filter(
                Q(phone=phone_or_email) | Q(email=phone_or_email)
            ).first()
            if check_user:
                phone_or_email = check_user.phone

            password = data.get('password')
            user = authenticate(phone=phone_or_email, password=password)
        if user and user.is_active and ((hasattr(user, "deleted") and user.deleted == False) or not hasattr(user, "deleted")):
            return user
        raise serializers.ValidationError("Incorrect Credentials")


class RegisterUserSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    class Meta:
        model = User
        fields = ('email', 'phone', 'password', 'name', 'church_profile', 'user_type',)
        extra_kwargs = {
            'password': {'write_only': True},  # Ensure the password is not included in responses
            'email': {'required': False},       # Email is required during registration
            'phone': {'required': True},       # Phone is required during registration
        }

    def validate(self, attrs):
        """Validate the data to ensure the email and phone are unique."""
        if User.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError("Email already exists")
        if User.objects.filter(phone=attrs.get('phone')).exists():
            raise serializers.ValidationError("Phone already exists")
        return attrs

    def create(self, validated_data):
        """Create a new user instance."""
        user = User.objects.create_user(
            phone=validated_data.get('phone'),
            email=validated_data.get('email'),
            password=validated_data.get('password'),
            name=validated_data.get('name'),
            church_profile=validated_data.get('church_profile'),
            user_type=validated_data.get('user_type'),
        )
        return user


class AddApplicationSerializers(serializers.ModelSerializer):
    '''Serializer for adding applications'''
    class Meta:
        model = Application
        fields = "__all__"

class RegionSerializer(serializers.ModelSerializer):
    '''Serializer for regions'''
    districts = serializers.ReadOnlyField()
    churches = serializers.ReadOnlyField()
    created_by_user = serializers.ReadOnlyField()
    class Meta:
        model = Region
        fields = "__all__"


class GetDistrictSerializer(serializers.ModelSerializer):
    '''Serializer for districts'''
    region = RegionSerializer()
    regions = serializers.ReadOnlyField()
    churches = serializers.ReadOnlyField()
    class Meta:
        model = District
        fields = "__all__"

class AddChurchSerializer(serializers.ModelSerializer):
    '''Serializer for adding churches'''
    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all())
    class Meta:
        model = Church
        fields = "__all__"

class GetChurchSerializer(serializers.ModelSerializer):
    '''Serializer for getting churches'''
    district = GetDistrictSerializer()
    class Meta:
        model = Church
        fields = "__all__"


class ApplicationSerializers(serializers.ModelSerializer):
    '''Serializer for applications'''
    church = GetChurchSerializer()
    class Meta:
        model = Application
        fields = "__all__"
        

class AddApplicationSerializers(serializers.ModelSerializer):
    '''Serializer for applications'''
    class Meta:
        model = Application
        fields = "__all__"
        
class AddRepaymentSerializer(serializers.ModelSerializer):
    '''Serializer for repayments'''
    class Meta:
        model = Repayment
        fields = "__all__"


class GetRepaymentSerializer(serializers.ModelSerializer):
    '''Serializer for repayments'''
    application = ApplicationSerializers()
    class Meta:
        model = Repayment
        fields = "__all__"


class AddProgressReportSerializer(serializers.ModelSerializer):
    '''Serializer for adding progress reports'''
    class Meta:
        model = ProgressReport
        fields = "__all__"

class GetProgressReportSerializer(serializers.ModelSerializer):
    '''Serializer for getting progress reports'''
    application = ApplicationSerializers()
    class Meta:
        model = ProgressReport
        fields = "__all__"

class AddDisbursementSerializer(serializers.ModelSerializer):
    '''Serializer for adding disbursements'''
    class Meta:
        model = Disbursement
        fields = "__all__"

class GetDisbursementSerializer(serializers.ModelSerializer):
    '''Serializer for getting disbursements'''
    application = ApplicationSerializers()
    class Meta:
        model = Disbursement
        fields = "__all__"

class AddDistrictSerializer(serializers.ModelSerializer):
    '''Serializer for districts'''
    region = serializers.PrimaryKeyRelatedField(queryset=Region.objects.all())
    class Meta:
        model = District
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer):
    '''Serializer for notifications'''
    class Meta:
        model = Notification
        fields = "__all__"


class ResetPasswordSerializer(serializers.Serializer):
    '''Serializer for resetting password'''
    phone = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        if not User.objects.filter(phone=data.get('phone')).exists():
            raise serializers.ValidationError("Phone does not exist")
        return data