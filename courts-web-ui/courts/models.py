from django.db import models


class DmCourtCases(models.Model):
    id = models.BigAutoField(primary_key=True)
    court = models.CharField(max_length=200, blank=True, null=True)
    court_alias = models.CharField(max_length=50, blank=True, null=True)
    check_date = models.DateField(blank=True, null=True)
    section_name = models.CharField(max_length=1000, blank=True, null=True)
    # order_num = models.IntegerField(blank=True, null=True)
    case_num = models.CharField(max_length=255, blank=True, null=True)
    hearing_time = models.CharField(max_length=50, blank=True, null=True)
    hearing_place = models.CharField(max_length=255, blank=True, null=True)
    case_info = models.CharField(max_length=10000, blank=True, null=True)
    stage = models.CharField(max_length=1000, blank=True, null=True)
    judge = models.CharField(max_length=255, blank=True, null=True)
    hearing_result = models.CharField(max_length=1000, blank=True, null=True)
    decision_link = models.CharField(max_length=1000, blank=True, null=True)
    case_link = models.CharField(max_length=1000, blank=True, null=True)
    row_hash = models.CharField(max_length=100, blank=True, null=True)
    load_dttm = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dm_v_court_cases'
        ordering = ['court_alias', 'court']
