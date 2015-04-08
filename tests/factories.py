import factory
import factory.fuzzy

from .models import BreadTestModel


class BreadTestModelFactory(factory.DjangoModelFactory):
    FACTORY_FOR = BreadTestModel

    name = factory.fuzzy.FuzzyText(length=10)
