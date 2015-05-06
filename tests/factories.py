import factory
import factory.fuzzy

from .models import BreadTestModel, BreadLabelValueTestModel


class BreadTestModelFactory(factory.DjangoModelFactory):
    FACTORY_FOR = BreadTestModel

    name = factory.fuzzy.FuzzyText(length=10)


class BreadLabelValueTestModelFactory(factory.DjangoModelFactory):
    FACTORY_FOR = BreadLabelValueTestModel

    name = factory.fuzzy.FuzzyText(length=10)
