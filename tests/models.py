"""
We really need models to test BREAD with, but Django's support for
defining test-only models is (still) broken.  See
https://code.djangoproject.com/ticket/7835 and scroll down to the
end (it's been open over 6 years).

So these models are here for the tests to use, but nothing else.
If Django ever gets this sorted out, we can move these models
to the tests, and maybe get fancier with different test models
for different tests.
"""
from django.db import models


class BreadLabelValueTestModel(models.Model):
    """Model for testing LabelValueReadView, also for GetVerboseNameTest"""

    name = models.CharField(max_length=10)
    banana = models.IntegerField(verbose_name="a yellow fruit", default=0)

    def name_reversed(self):
        return self.name[::-1]


class BreadTestModel2(models.Model):
    text = models.CharField(max_length=20)
    label_model = models.OneToOneField(
        BreadLabelValueTestModel,
        null=True,
        related_name="model2",
        on_delete=models.CASCADE,
    )
    model1 = models.OneToOneField(
        "BreadTestModel",
        null=True,
        related_name="model1",
        on_delete=models.CASCADE,
    )

    def get_text(self):
        return self.text


class BreadTestModel(models.Model):
    name = models.CharField(max_length=10)
    age = models.IntegerField()
    other = models.ForeignKey(
        BreadTestModel2,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = [
            "name",
            "-age",  # If same name, sort oldest first
        ]
        permissions = [
            ("browse_breadtestmodel", "can browse BreadTestModel"),
        ]

    def __str__(self):
        return self.name

    def get_name(self):
        return self.name

    def method1(self, arg):
        # Method that has a required arg
        pass

    def method2(self, arg=None):
        # method that has an optional arg
        pass
