from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from airport.models import Aircraft, StateChangeLog
from airport.serializers import AircraftSerializer, LocationSerializer, StateChangeLogSerializer
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

        intent = request.data.get('intent', None)
        state = request.data.get('state', None)
        if intent:
            state = intent

        data = {
            'call_sign': call_sign,
            'state': state,
            'type': request.data.get('type', None),
            'longitude': request.data.get('longitude', 0),
            'latitude': request.data.get('latitude', 0),
            'altitude': request.data.get('altitude', 0),
            'heading': request.data.get('heading', 0),
        }

        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            state_from = ''
            state_to = ''
            try:
                aircraft = Aircraft.objects.get(call_sign=call_sign)
                state_from = aircraft.state
                state_to = data['state']
            except Aircraft.DoesNotExist:
                aircraft = Aircraft(**serializer.data)
                state_from = request.data.get('state', None)
                state_to = request.data.get('intent', None)
                aircraft.state = state_to
                aircraft.save()

            log = StateChangeLog(
                aircraft=aircraft,
                from_state=state_from,
                to_state=state_to,
                outcome='ACCEPTED'
            )

            aircraft.state = serializer.data['state']
            aircraft.save()

            log.save()

            return Response(None, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

    def handle_exception(self, exc):
        if isinstance(exc, (StateConflict,)):
            if exc.aircraft:
                StateChangeLog.objects.create(
                    aircraft=exc.aircraft,
                    from_state=exc.from_state,
                    to_state=exc.to_state,
                    description=exc.description,
                    outcome='REJECTED'
                )
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


class StateChangeLogViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = StateChangeLogSerializer
    queryset = StateChangeLog.objects.all().order_by('-time')
    pagination_class = LimitOffsetPagination


class StartSimulationViewSet(viewsets.GenericViewSet):
    """ This view is used for demo purposes only to easily exercise an API.
    It will remove all existing aircrafts and state change logs from the system.
    """

    queryset = Aircraft.objects.all()
    permission_classes = [IsValidPublicKey]

    @action(methods=['post'], detail=False,
            url_path='start',
            url_name='start_simulation')
    def start_simulation(self, request, *args):
        Aircraft.objects.all().delete()
        Aircraft.objects.create(
            call_sign='CYAN',
            type="PRIVATE",
            state="PARKED"
        )
        return Response()
