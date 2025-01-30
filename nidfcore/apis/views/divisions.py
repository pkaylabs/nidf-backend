from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import District, Region
from apis.serializers import AddDistrictSerializer, GetDistrictSerializer, RegionSerializer
from nidfcore.utils.constants import UserType


class RegionsAPIView(APIView):
    '''Endpoint for getting and creating regions'''

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        # anyone user can get all regions
        regions = Region.objects.all().order_by('name')
        serializer = RegionSerializer(regions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        user = request.user
        name = request.data.get('name')
        region = Region.objects.filter(name=name).first()

        serializer = RegionSerializer(region, data=request.data)

        if user.user_type == UserType.CHURCH_USER.value:
            return Response({"message": "You are not allowed to create regions"}, status=status.HTTP_401_UNAUTHORIZED)

        if serializer.is_valid():
            serializer.save()
            if region is None:
                return Response({"message": "Region created successfully"}, status=status.HTTP_201_CREATED)
            return Response({"message": "Region Upudated successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DistrictsAPIView(APIView):
    '''Endpoint for getting and creating districts'''

    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        # anyone at all can get districts
        districts = District.objects.all().order_by('name')
        serializer = GetDistrictSerializer(districts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        user = request.user
        name = request.data.get('name')
        district = District.objects.filter(name=name).first()

        serializer = AddDistrictSerializer(district, data=request.data)

        if user.user_type == UserType.CHURCH_USER.value:
            return Response({"message": "You are not allowed to create district"}, status=status.HTTP_401_UNAUTHORIZED)

        if serializer.is_valid():
            serializer.save()
            if district is None:
                return Response({"message": "District created successfully"}, status=status.HTTP_201_CREATED)
            return Response({"message": "District Upudated successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)