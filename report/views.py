import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.translation import gettext as _

from report.services import get_report_definition, generate_report
from .apps import ReportConfig

logger = logging.getLogger(__file__)


def report(request, module_name, report_name, report_format="pdf", alternate=None):
    """
    Run a report
    :param request: Predefined by Django
    :param module_name: Name of the module with the requested report
    :param report_name: Report name within the module
    :param report_format: pdf (default) or xlsx
    :param alternate: Future use, allows several templates for a single report: different languages or report variants
    :return: view
    """
    logger.debug("report name %s in module %s in %s format", report_name, module_name, report_format)
    report_config = ReportConfig.get_report(module_name, report_name)
    if not report_config:
        raise Http404("Poll does not exist")
    report_definition = get_report_definition(report_name, report_config["default_report"])
    # parameters tend to get put in lists because they *could* be repeated
    unlisted = {k: (v[0] if isinstance(v, list) and len(v) == 0 else v) for k, v in request.GET.items()}

    # TODO enable with latest JWT PR
    # if report_config.get("permission") and \
    #         not request.user.has_perms(ReportConfig.gql_query_report_perms) and \
    #         not request.user.has_perms(report_config.get("permission")):
    #     raise PermissionDenied(_("unauthorized"))

    data = report_config["python_query"](request.user, **unlisted)

    return generate_report(
        report_name,
        report_definition,
        data,
        report_format,
    )
