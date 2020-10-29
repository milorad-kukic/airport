from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from Crypto.PublicKey import RSA

from airport.models import Aircraft
from airport.serializers import AircraftSerializer


class AircraftViewSet(viewsets.GenericViewSet):
    queryset = Aircraft.objects.all()
    serializer_class = AircraftSerializer

    @action(methods=['post'], detail=False,
            url_path='(?P<call_sign>[^/.]+)/intent',
            url_name='intent')
    def intent(self, request, call_sign=None, pk=None):
        public_key = request.data.get('public_key', None)

        if not public_key or not public_key_is_valid(public_key):
            return Response(None, status=status.HTTP_401_UNAUTHORIZED)

        if not request.data.get('public_key', None):
            return Response(None, status=status.HTTP_401_UNAUTHORIZED)

        data = {
            'call_sign': call_sign,
            'state': request.data.get('state', None)
        }

        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            try:
                aircraft = Aircraft.objects.get(call_sign=call_sign)
            except Aircraft.DoesNotExist:
                aircraft = Aircraft.objects.create(**serializer.data)

            aircraft.state = serializer.data['state']
            aircraft.save()

            return Response(None, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)


def public_key_is_valid(public_key_content):
    """ This method will answer if given public key matches
    a given private key or not"""

    private_key = None

    with open("/keys/airport_ops_rsa") as private_key_file:
        private_key = RSA.importKey(private_key_file.read())

    if not private_key:
        return False

    public_key = RSA.importKey(public_key_content)

    return private_key.publickey() == public_key
