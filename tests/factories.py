import factory
import factory.fuzzy

from .models import BreadLabelValueTestModel, BreadTestModel, BreadTestModel2


class BreadTestModel2Factory(factory.DjangoModelFactory):
    FACTORY_FOR = BreadTestModel2

    text = factory.fuzzy.FuzzyText(length=10)


class BreadTestModelFactory(factory.DjangoModelFactory):
    FACTORY_FOR = BreadTestModel

    name = factory.fuzzy.FuzzyText(length=10)
    age = factory.fuzzy.FuzzyInteger(low=1, high=99)
    other = factory.SubFactory(BreadTestModel2Factory)


class BreadLabelValueTestModelFactory(factory.DjangoModelFactory):
    FACTORY_FOR = BreadLabelValueTestModel

    name = factory.fuzzy.FuzzyText(length=10)
