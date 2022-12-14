# Generated by Django 4.1.4 on 2023-01-08 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DmCourtCases",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("court", models.CharField(blank=True, max_length=200, null=True)),
                ("court_alias", models.CharField(blank=True, max_length=50, null=True)),
                ("check_date", models.DateField(blank=True, null=True)),
                (
                    "section_name",
                    models.CharField(blank=True, max_length=1000, null=True),
                ),
                ("case_num", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "hearing_time",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "hearing_place",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "case_info",
                    models.CharField(blank=True, max_length=10000, null=True),
                ),
                ("stage", models.CharField(blank=True, max_length=1000, null=True)),
                ("judge", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "hearing_result",
                    models.CharField(blank=True, max_length=1000, null=True),
                ),
                (
                    "decision_link",
                    models.CharField(blank=True, max_length=1000, null=True),
                ),
                ("case_link", models.CharField(blank=True, max_length=1000, null=True)),
                ("row_hash", models.CharField(blank=True, max_length=100, null=True)),
                ("load_dttm", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "db_table": "dm_v_court_cases",
                "ordering": ["court_alias", "court"],
                "managed": False,
            },
        ),
    ]
