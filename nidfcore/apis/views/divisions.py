from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Church, District, Region
from apis.serializers import (AddDistrictSerializer, GetChurchSerializer,
                              GetDistrictSerializer, RegionSerializer)
from nidfcore.utils.constants import UserType


class RegionsAPIView(APIView):
    '''Endpoint for getting and creating regions'''

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        # anyone user can get all regions or a single region if a param is parsed
        param = request.query_params.get('query')
        divisions = District.objects.none() 
        if param == None:
            regions = Region.objects.all().order_by('name')
            many = True
        else:
            regions = Region.objects.filter(name=param).first()
            if regions is not None:
                divisions = District.objects.filter(region=regions)
            many = False
        serializer = RegionSerializer(regions, many=many)
        district_serializer = GetDistrictSerializer(divisions, many=True)

        return Response({"region":serializer.data, "divisions":district_serializer.data }, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        user = request.user
        name = request.data.get('name')
        region = Region.objects.filter(name=name).first()

        serializer = RegionSerializer(region, data=request.data)

        if user.user_type == UserType.CHURCH_USER.value:
            return Response({"message": "You are not allowed to create regions"}, status=status.HTTP_401_UNAUTHORIZED)

        if serializer.is_valid():
            serializer.save(created_by=user)
            if region is None:
                return Response({"message": "Region created successfully"}, status=status.HTTP_201_CREATED)
            return Response({"message": "Region Updated successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    def delete(self, request, *args, **kwargs):
        # only admin users can delete regions
        user = request.user
        if not (user.user_type == UserType.ADMIN.value or user.is_superuser or user.is_staff ):
            return Response({"message": "You are not allowed to delete regions"}, status=status.HTTP_401_UNAUTHORIZED)
        region_id = request.data.get('region')
        region = Region.objects.filter(id=region_id).first()
        if region is None:
            return Response({"message": "Region not found"}, status=status.HTTP_404_NOT_FOUND)
        region.delete()
        return Response({"message": "Region deleted successfully"}, status=status.HTTP_200_OK)


class DivisionsAPIView(APIView):
    '''Endpoint for getting and creating divisions'''

    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        # we can use this endpoint to get all or a single district by parsing 
        # the name of the district as a 'query' param.
        param = request.query_params.get('query')
        churches = Church.objects.none()
        if param == None:
            divisions = District.objects.all().order_by('name')
            many = True
        else:
            divisions = District.objects.filter(name=param).first()
            if divisions is not None:
                churches = Church.objects.filter(district=divisions)
            many = False
        divisions = District.objects.all().order_by('name')
        serializer = GetDistrictSerializer(divisions, many=many)
        church_serializer = GetChurchSerializer(churches, many=True)

        return Response({"divisions":serializer.data, "churches":church_serializer.data }, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        user = request.user
        name = request.data.get('name')
        district = District.objects.filter(name=name).first()

        serializer = AddDistrictSerializer(district, data=request.data)

        if user.user_type == UserType.CHURCH_USER.value:
            return Response({"message": "You are not allowed to create division"}, status=status.HTTP_401_UNAUTHORIZED)

        if serializer.is_valid():
            serializer.save()
            if district is None:
                return Response({"message": "Division created successfully"}, status=status.HTTP_201_CREATED)
            return Response({"message": "Division Upudated successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, *args, **kwargs):
        # only admin users can delete divisions
        user = request.user
        if not (user.user_type == UserType.ADMIN.value or user.is_superuser or user.is_staff ):
            return Response({"message": "You are not allowed to delete devision"}, status=status.HTTP_401_UNAUTHORIZED)
        division_id = request.data.get('division')
        division = District.objects.filter(id=division_id).first()
        if division is None:
            return Response({"message": "Division not found"}, status=status.HTTP_404_NOT_FOUND)
        division.delete()
        return Response({"message": "Division deleted successfully"}, status=status.HTTP_200_OK)