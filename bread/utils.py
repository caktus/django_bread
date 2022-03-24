"""
Django has a convenient notation to refer to a
field on a model, even when referenced via one or
more foreign key links:

https://docs.djangoproject.com/en/dev/topics/db/queries/#lookups-that-span-relationships

E.g. if you have a model with a "link" field that's
a foreign key to another model with a "name" field, you
can refer to that "name" field in a query as
"link__name"

The get_model_field method below allows you to do
the same thing in your own code -- you could get the
value of that "name" field using

    get_model_field(my_model_instance, "link__name")

Of course you could just write ``my_model_instance.link.name``
if you already knew the field names, but this is helpful for
things like the "search" parameter in the admin that give
a list of strings that need to refer to possibly nested
model fields.

This provides an additional feature over the lookup syntax
in queryset filters: if the object that the string eventually
resolves to is a callable, it will be called to get its return
value, similar to how references to context variables in templates
work.
"""
import inspect

from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.db.models import Model
from django.db.models.fields.related import RelatedField
from django.db.models.fields.reverse_related import OneToOneRel


def get_value_or_result(model_instance, attribute_name):
    attr = getattr(model_instance, attribute_name)
    if callable(attr):
        return attr()
    return attr


def get_model_field(model_instance, spec):
    if model_instance is None:
        raise ValueError("None passed into get_model_field")
    if not isinstance(model_instance, Model):
        raise ValueError(
            "%r should be an instance of a model but it is a %s"
            % (model_instance, type(model_instance))
        )

    if spec.startswith("__") and spec.endswith("__"):
        # It's a dunder method; don't split it.
        name_parts = [spec]
    else:
        name_parts = spec.split("__", 1)

    value = getattr(model_instance, name_parts[0])
    if callable(value):
        value = value()
    if len(name_parts) > 1 and value is not None:
        return get_model_field(value, name_parts[1])
    return value


def get_verbose_name(an_object, field_name, title_cap=True):
    """Given a model or model instance, return the verbose_name of the model's field.

    If title_cap is True (the default), the verbose_name will be returned with the first letter
    of each word capitalized which makes the verbose_name look nicer in labels.

    If field_name doesn't refer to a model field, raises a FieldDoesNotExist error.
    """
    # get_field() can raise FieldDoesNotExist which I simply propogate up to the caller.
    try:
        field = an_object._meta.get_field(field_name)
    except TypeError:
        # TypeError happens if the caller is very confused and passes an unhashable type such
        # as {} or []. I convert that into a FieldDoesNotExist exception for simplicity.
        raise FieldDoesNotExist("No field named {}".format(str(field_name)))

    verbose_name = field.verbose_name

    if title_cap:
        # Title cap the label using this stackoverflow-approved technique:
        # http://stackoverflow.com/questions/1549641/how-to-capitalize-the-first-letter-of-each-word-in-a-string-python
        verbose_name = " ".join(word.capitalize() for word in verbose_name.split())

    return verbose_name


def has_required_args(func):
    """
    Return True if the function has any required arguments.
    """
    spec = inspect.getfullargspec(func)
    num_args = len(spec.args)
    # If first arg is 'self', we can ignore one arg
    if num_args and spec.args[0] == "self":
        num_args -= 1
    # If there are defaults, we can ignore the same number of args
    if spec.defaults:
        num_args -= len(spec.defaults)
    # Do we still have args without defaults?
    return num_args > 0


def validate_fieldspec(model, spec):
    """
    Given a model class and a string that refers to a possibly nested
    field on that model (as used in `get_model_field`).

    Raises a ValidationError with a useful error message if the spec
    does not appear to be valid.

    Otherwise just returns.
    """
    if not issubclass(model, Model):
        raise TypeError(
            "First argument to validate_fieldspec must be a "
            "subclass of Model; it is %r" % model
        )
    parts = spec.split("__", 1)
    rest_of_spec = parts[1] if len(parts) > 1 else None

    # What are the possibilities for what parts[0] is on our model?
    # - It could be a field
    #   - simple (not a key)
    #   - key
    # - It could be a non-field
    #   - class variable
    #   - method
    # - It could not exist

    try:
        field = model._meta.get_field(parts[0])
    except FieldDoesNotExist:
        # Not a field - is there an attribute of some sort?
        if not hasattr(model, parts[0]):
            raise ValidationError(
                "There is no field or attribute named '%s' on model '%s'"
                % (parts[0], model)
            )
        if rest_of_spec:
            raise ValidationError(
                "On model '%s', '%s' is not a field, but the spec tries to refer through "
                "it to '%s'." % (model, parts[0], rest_of_spec)
            )
        attr = getattr(model, parts[0])
        if callable(attr):
            if has_required_args(attr):
                raise ValidationError(
                    "On model '%s', '%s' is callable and has required arguments; it is not "
                    "valid to use in a field spec" % (model, parts[0])
                )
    else:
        # It's a field
        # Is it a key?
        if isinstance(field, RelatedField) or isinstance(field, OneToOneRel):
            # Yes, refers to another model
            if rest_of_spec:
                # Recurse!
                validate_fieldspec(model=field.related_model, spec=rest_of_spec)
            # Well, it's okay if it just returns a reference to another record
        else:
            # Simple field
            # Is there more spec?
            if rest_of_spec:
                raise ValidationError(
                    "On model '%s', '%s' is not a key field, but the spec tries to refer through "
                    "it to '%s'." % (model, parts[0], rest_of_spec)
                )
            # Simple field, no more spec, looks good
