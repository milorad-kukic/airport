from Crypto.PublicKey import RSA

from rest_framework.permissions import BasePermission

from airport.exceptions import InvalidPublicKey


class IsValidPublicKey(BasePermission):
    """Custom permission class which will check if provided
    public key is in pair with used private key."""

    def __init__(self):
        self.private_key = None

    def has_permission(self, request, view):
        with open("/keys/airport_ops_rsa") as private_key_file:
            self.private_key = RSA.importKey(private_key_file.read())
        if not self.private_key:
            raise InvalidPublicKey()

        public_key_content = request.data.get('public_key', None)

        if not public_key_content:
            raise InvalidPublicKey()

        public_key = RSA.importKey(public_key_content)

        if not self.private_key.publickey() == public_key:
            raise InvalidPublicKey()

        return True

    def public_key_is_valid(self, public_key_content):
        """ This method will answer if given public key matches
        a given private key or not"""

        private_key = None

        with open("/keys/airport_ops_rsa") as private_key_file:
            private_key = RSA.importKey(private_key_file.read())

        if not private_key:
            return False

        public_key = RSA.importKey(public_key_content)

        return private_key.publickey() == public_key
