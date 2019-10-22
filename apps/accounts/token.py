from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six

##### https://medium.com/@frfahim/django-registration-with-confirmation-email-bb5da011e4ef 

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.banned)
        )
account_activation_token = TokenGenerator()