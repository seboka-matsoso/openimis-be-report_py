from django.db import models
from core import models as core_models

from core.models import UUIDVersionedModel


class ReportDefinition(core_models.UUIDModel, UUIDVersionedModel):
    """
    Record report (business modules) templates to be generated by the templating engine (reportbro for PDF,...)
    Initial implementation only integrate ReportBro templating engine
    """

    REPORT_BRO = 0
    REPORT_ENGINE_CHOICES = ((REPORT_BRO, "Report Bro - PDF"),)

    name = models.CharField(max_length=255, blank=False, null=False)
    # alternate_of = models.CharField(
    #     max_length=255, blank=True, null=True
    # )
    engine = models.IntegerField(choices=REPORT_ENGINE_CHOICES, default=REPORT_BRO)
    definition = models.TextField()

    class Meta:
        managed = True
        db_table = "report_ReportDefinition"


class GeneratedReports(models.Model):
    id = models.AutoField(db_column="ReportingId", primary_key=True)
    reporting_date = models.TextField(db_column="ReportingDate")
    location = models.ForeignKey(
        "location.Location", models.DO_NOTHING, db_column="LocationId", related_name="+"
    )
    product = models.ForeignKey(
        "product.Product", models.DO_NOTHING, db_column="ProdId", related_name="+"
    )
    payer = models.ForeignKey(
        "payer.Payer",
        models.DO_NOTHING,
        db_column="PayerId",
        blank=True,
        null=True,
        related_name="generated_reports",
    )
    start_date = models.DateField(db_column="StartDate")
    end_date = models.DateField(db_column="EndDate")
    record_found = models.IntegerField(db_column="RecordFound")
    officer = models.ForeignKey(
        "core.Officer",
        on_delete=models.DO_NOTHING,
        db_column="OfficerID",
        null=True,
        blank=True,
    )
    report_type = models.IntegerField(db_column="ReportType", null=True, blank=True)
    commission_rate = models.DecimalField(
        db_column="CommissionRate",
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
    )
    report_mode = models.IntegerField(
        db_column="ReportMode", default=0, null=True, blank=True
    )
    scope = models.IntegerField(db_column="Scope", null=True, blank=True)

    # Used by Overview of Commissions
    REPORT_MODE_PRESCRIBED = 0
    REPORT_MODE_PAID = 1

    class Meta:
        managed = True
        db_table = "tblReporting"
