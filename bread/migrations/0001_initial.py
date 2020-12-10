# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BreadTestModel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=10)),
            ],
            options={
                "ordering": ["name"],
                "permissions": [("browse_breadtestmodel", "can browse BreadTestModel")],
            },
            bases=(models.Model,),
        ),
    ]
