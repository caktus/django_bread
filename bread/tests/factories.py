import factory
import factory.fuzzy

from bread.models import BreadTestModel


class BreadTestModelFactory(factory.DjangoModelFactory):
    FACTORY_FOR = BreadTestModel

    name = factory.fuzzy.FuzzyText(length=10)
