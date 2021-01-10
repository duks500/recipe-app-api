from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users objects"""

    class Meta:
        model = get_user_model()
        # the fields that are going to be accessiable in the API
        fields = ('email', 'password', 'name')
        # Check if the passwordis longer or equal to 5 characters (restricet)
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        # Pop is very simalr to get
        password = validated_data.pop('password', None)
        # Take the default and custimaze it
        user = super().update(instance, validated_data)

        # Set the password
        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication objects"""
    email = serializers.CharField()
    password = serializers.CharField(
        # Style
        style={
            'input_type': 'password'
        },
        # Do not trip the whitespace if included
        trim_whitespace=False
    )

    # Checking that the imputs are correct
    # attrs = is any field in the serializer
    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            # Pass the request
            request=self.context.get('request'),
            # Pass the username
            username=email,
            password=password
        )
        # check if did not work (authentication failed)
        # if yes-> print a message
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        # User attrs is set to be equal to the user
        attrs['user'] = user
        return attrs
