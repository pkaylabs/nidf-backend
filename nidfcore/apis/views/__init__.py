from .applications import *
from .disbursements import *
from .repayments import *
from .subdivisions import *
from .users import *


class PingAPI(APIView):
    '''An endpoint to test if the API is up and running'''
    def get(self, request):
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)