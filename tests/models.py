"""
We really need a model to test BREAD with, but Django's support for
defining test-only models is (still) broken.  See
https://code.djangoproject.com/ticket/7835 and scroll down to the
end (it's been open over 6 years).

So this model is here for the tests to use, but nothing else.
If Django ever gets this sorted out, we can move this model
to the tests, and maybe get fancier with different test models
for different tests.
"""
from __future__ import unicode_literals
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


class BreadTestModel2(models.Model):
    text = models.CharField(max_length=20)

    def get_text(self):
        return self.text


@python_2_unicode_compatible
class BreadTestModel(models.Model):
    name = models.CharField(max_length=10)
    other = models.ForeignKey(BreadTestModel2, blank=True, null=True)

    class Meta:
        ordering = ['name']
        permissions = [
            ('read_breadtestmodel', 'can read BreadTestModel'),
            ('browse_breadtestmodel', 'can browse BreadTestModel'),
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
