# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bread', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BreadTestModel',
        ),
    ]
