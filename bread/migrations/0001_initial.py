# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BreadTestModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=10)),
            ],
            options={
                'ordering': ['name'],
                'permissions': [('read_breadtestmodel', 'can read BreadTestModel'), ('browse_breadtestmodel', 'can browse BreadTestModel')],
            },
            bases=(models.Model,),
        ),
    ]
