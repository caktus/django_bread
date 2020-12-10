import logging

from django import template
from django.core.exceptions import ObjectDoesNotExist

from bread.utils import get_model_field

logger = logging.getLogger(__name__)
register = template.Library()


@register.filter(name="getter")
def getter(value, arg):
    """
    Given an object `value`, return the value of the attribute named `arg`.
    `arg` can contain `__` to drill down recursively into the values.
    If the final result is a callable, it is called and its return
    value used.
    """
    try:
        return get_model_field(value, arg)
    except ObjectDoesNotExist:
        pass
    except Exception:
        logger.exception("Something blew up: %s|getter:%s" % (value, arg))
