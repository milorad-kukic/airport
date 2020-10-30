
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from airport.models import Aircraft
from airport.serializers import AircraftSerializer, LocationSerializer
from airport.permissions import IsValidPublicKey
from airport.exceptions import StateConflict


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
            'state': request.data.get('state', None),
            'longitude': request.data.get('longitude', 0),
            'latitude': request.data.get('latitude', 0),
            'altitude': request.data.get('altitude', 0),
            'heading': request.data.get('heading', 0),
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

    def handle_exception(self, exc):
        if isinstance(exc, (StateConflict,)):
            response = Response(None, status=exc.status_code)
        else:
            response = super().handle_exception(exc)

        return response

    @action(methods=['post'], detail=False,
            url_path='(?P<call_sign>[^/.]+)/location',
            url_name='location')
    def location(self, request, call_sign=None, pk=None):

        aircraft = Aircraft.objects.get(call_sign=call_sign)

        data = {
            'call_sign': call_sign,
            'type': request.data.get('type', None),
            'longitude': request.data.get('longitude', None),
            'latitude': request.data.get('latitude', None),
            'altitude': request.data.get('altitude', None),
            'heading': request.data.get('heading', None)
        }
        serializer = LocationSerializer(data=data)

        if serializer.is_valid():
            for k, v in data.items():
                setattr(aircraft, k, v)
            aircraft.save()

            return Response(None, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)
