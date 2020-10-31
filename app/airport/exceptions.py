from rest_framework.exceptions import APIException
from rest_framework import status


class InvalidPublicKey(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = ''
    default_code = ''


class StateConflict(APIException):
    status_code = status.HTTP_409_CONFLICT

    def __init__(self, aircraft, from_state, to_state):
        self.aircraft = aircraft
        self.from_state = from_state
        self.to_state = to_state
