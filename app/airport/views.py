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

        try:
            Aircraft.objects.get(call_sign=call_sign)
        except Aircraft.DoesNotExist:
            Aircraft.objects.create(call_sign=call_sign)

        return Response(None, status=status.HTTP_204_NO_CONTENT)


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
