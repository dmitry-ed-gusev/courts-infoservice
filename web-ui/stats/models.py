from django.db import models


class DmVCourtCaseStatsDetail(models.Model):
    court_alias = models.CharField(unique=True, max_length=50, primary_key=True)
    title = models.CharField(max_length=1000, blank=True, null=True)
    total_rows = models.IntegerField(blank=True, null=True)
    min_dt = models.DateField(blank=True, null=True)
    max_dt = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dm_v_court_case_stats_detail'
        ordering = ['court_alias']
