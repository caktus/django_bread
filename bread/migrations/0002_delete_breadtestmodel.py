# -*- coding: utf-8 -*-
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("bread", "0001_initial"),
    ]

    operations = [
        migrations.DeleteModel(
            name="BreadTestModel",
        ),
    ]
