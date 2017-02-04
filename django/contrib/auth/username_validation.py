import functools

from django.conf import settings
from django.core.exceptions import (
    ImproperlyConfigured, ValidationError,
)
from django.utils.functional import lazy
from django.utils.html import format_html
from django.utils.module_loading import import_string
from django.utils.translation import ugettext as _, ungettext


@functools.lru_cache(maxsize=None)
def get_default_username_validators():
    return get_username_validators(settings.AUTH_USERNAME_VALIDATORS)


def get_username_validators(validator_config):
    validators = []
    for validator in validator_config:
        try:
            klass = import_string(validator['NAME'])
        except ImportError:
            msg = "The module in NAME could not be imported: %s. Check your AUTH_USERNAME_VALIDATORS setting."
            raise ImproperlyConfigured(msg % validator['NAME'])
        validators.append(klass(**validator.get('OPTIONS', {})))

    return validators


def username_validators_help_texts(username_validators=None):
    """
    Return a list of all help texts of all configured validators.
    """
    help_texts = []
    if username_validators is None:
        username_validators = get_default_username_validators()
    for validator in username_validators:
        help_texts.append(validator.message)
    return help_texts


def _username_validators_help_text_html(username_validators=None):
    """
    Return an HTML string with all help texts of all configured validators
    in an <ul>.
    """
    help_texts = username_validators_help_texts(username_validators)
    help_items = [format_html('<li>{}</li>', help_text) for help_text in help_texts]
    return '<ul>%s</ul>' % ''.join(help_items) if help_items else ''


username_validators_help_text_html = lazy(_username_validators_help_text_html, str)
