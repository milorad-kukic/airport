
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from airport.models import Aircraft
from airport.serializers import AircraftSerializer
from airport.permissions import IsValidPublicKey


class AircraftViewSet(viewsets.GenericViewSet):
    queryset = Aircraft.objects.all()
    serializer_class = AircraftSerializer
    permission_classes = [IsValidPublicKey]

    @action(methods=['post'], detail=False,
            url_path='(?P<call_sign>[^/.]+)/intent',
            url_name='intent')
    def intent(self, request, call_sign=None, pk=None):
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
