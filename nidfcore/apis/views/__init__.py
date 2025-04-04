from .applications import *
from .churches import *
from .dashboard import *
from .disbursements import *
from .divisions import *
from .progressreport import *
from .repayments import *
from .users import *
from .notifications import *


class PingAPI(APIView):
    '''An endpoint to test if the API is up and running'''
    def get(self, request):
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)