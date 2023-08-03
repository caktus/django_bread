import factory

from .models import BreadLabelValueTestModel, BreadTestModel, BreadTestModel2


class BreadTestModel2Factory(factory.django.DjangoModelFactory):
    class Meta:
        model = BreadTestModel2

    text = factory.Faker("text", max_nb_chars=10)


class BreadTestModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BreadTestModel

    name = factory.Faker("name")
    age = factory.Faker("pyint", min_value=0, max_value=99)
    other = factory.SubFactory(BreadTestModel2Factory)


class BreadLabelValueTestModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BreadLabelValueTestModel

    name = factory.Faker("name")
