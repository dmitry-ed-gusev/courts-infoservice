# Generated by Django 4.1.4 on 2023-01-08 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stats", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DmVCourtCaseStatsDetail",
            fields=[
                (
                    "court_alias",
                    models.CharField(
                        max_length=50, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("title", models.CharField(blank=True, max_length=1000, null=True)),
                ("total_rows", models.IntegerField(blank=True, null=True)),
                ("min_dt", models.DateField(blank=True, null=True)),
                ("max_dt", models.DateField(blank=True, null=True)),
            ],
            options={
                "db_table": "dm_v_court_case_stats_detail",
                "ordering": ["court_alias"],
                "managed": False,
            },
        ),
        migrations.DeleteModel(
            name="DmVCourtStats",
        ),
    ]