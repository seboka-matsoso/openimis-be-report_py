import graphene

from core.schema import OpenIMISMutation
from report.apps import ReportConfig
from report.models import ReportDefinition
from core import ExtendedConnection
import graphene
from graphene.relay import Node
from django.utils.translation import gettext_lazy
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth.models import AnonymousUser
import graphene_django_optimizer as gql_optimizer
from django.utils.translation import gettext as _

from report.services import get_report_definition

import logging

logger = logging.getLogger(__file__)


class ReportDefinitionGQLType(DjangoObjectType):
    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.filter(validity_to=None)

    class Meta:
        model = ReportDefinition
        interfaces = (Node,)
        filter_fields = {
            "id": ["exact"],
            "name": ["exact", "icontains"],
        }
        connection_class = ExtendedConnection


class ReportGQLType(graphene.ObjectType):
    name = graphene.String()
    default_report = graphene.String()
    definition = graphene.String()
    description = graphene.String()
    module = graphene.String()
    permission = graphene.String()

    def resolve_definition(self, info, **kwargs):
        return get_report_definition(self.get("name"), self.get("default_report"))


class Query(graphene.ObjectType):
    report_definitions = DjangoFilterConnectionField(
        ReportDefinitionGQLType,
        show_history=graphene.Boolean(),
        search=graphene.String(description=gettext_lazy("Search in `name` & `code`")),
    )
    report_definition = graphene.Field(
        ReportDefinitionGQLType, id=graphene.ID(), uuid=graphene.String()
    )
    reports = graphene.List(ReportGQLType)
    report = graphene.Field(ReportGQLType, name=graphene.String(required=True))

    def resolve_reports(self, info, **kwargs):
        return [report for report in ReportConfig.reports]

    def resolve_report(self, info, name, **kwargs):
        for report in ReportConfig.reports:
            if report.get("name") == name:
                return report

    def resolve_report_definition(self, info, **kwargs):
        # if not info.context.user.has_perms(ReportConfig.gql_query_report_definitions_perms):
        #     raise PermissionDenied(_("unauthorized"))
        if kwargs.get("id", None) is not None:
            return Node.get_node_from_global_id(info, kwargs["id"])
        elif kwargs.get("uuid", None) is not None:
            return ReportDefinition.objects.get(id=kwargs["uuid"])

        return None

    def resolve_report_definitions(
        self, info, search=None, show_history=False, **kwargs
    ):
        # if not info.context.user.has_perms(ReportConfig.gql_query_report_definitions_perms):
        #     raise PermissionDenied(_("unauthorized"))

        qs = ReportDefinition.objects
        # if not show_history:
        #     qs = qs.filter(*filter_validity(**kwargs))

        # if search is not None:
        #     qs = qs.filter(Q(name__icontains=search) | Q(code__icontains=search))

        # if location is not None:
        #     from location.models import Location
        #
        #     qs = qs.filter(
        #         Q(location__in=Location.objects.parents(location))
        #         | Q(location__id=location)
        #     )

        return gql_optimizer.query(qs, info)


def update_or_create_report_definition(data, user):
    data.pop("client_mutation_id", None)
    data.pop("client_mutation_label", None)
    report_definition_uuid = data.pop("uuid", None)
    if report_definition_uuid:
        report_definition = ReportDefinition.objects.get(uuid=report_definition_uuid)
        # reset_report_definition_before_update(report_definition)
        [setattr(report_definition, k, v) for k, v in data.items()]
    else:
        report_definition = ReportDefinition.objects.create(**data)
    report_definition.save()
    return report_definition


class ReportDefinitionInputType(OpenIMISMutation.Input):
    id = graphene.Int(required=False, read_only=True)
    name = graphene.String(required=True, max_length=255)
    engine = graphene.Int(required=False)  # Always 0 for ReportBro for now
    definition = graphene.String(required=True)
    validity_from = graphene.DateTime(required=False)


class CreateReportDefinitionMutation(OpenIMISMutation):
    """
    Create a new Report Definition Override (the default is provided by the report itself)
    """

    _mutation_module = "report"
    _mutation_class = "CreateReportDefinitionMutation"

    class Input(ReportDefinitionInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            if type(user) is AnonymousUser or not user.id:
                raise ValidationError(_("mutation.authentication_required"))
            # if not user.has_perms(ReportConfig.gql_mutation_create_families_perms):
            #     raise PermissionDenied(_("unauthorized"))
            # data['audit_user_id'] = user.id_for_audit

            from core.utils import TimeUtils

            if "validity_from" not in data:
                data["validity_from"] = TimeUtils.now()
            update_or_create_report_definition(data, user)
            return None
        except Exception as exc:
            logger.exception("report.mutation.failed_to_create_report_definition")
            return [
                {
                    "message": _("report.mutation.failed_to_create_report_definition"),
                    "detail": str(exc),
                }
            ]


class UpdateReportDefinitionMutation(OpenIMISMutation):
    """
    Update an existing Report Definition Override (the default is provided by the report itself)
    """

    _mutation_module = "report"
    _mutation_class = "UpdateReportDefinitionMutation"

    class Input(ReportDefinitionInputType):
        uuid = graphene.String(required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            if type(user) is AnonymousUser or not user.id:
                raise ValidationError(_("mutation.authentication_required"))
            # if not user.has_perms(ReportConfig.gql_mutation_create_families_perms):
            #     raise PermissionDenied(_("unauthorized"))
            # data['audit_user_id'] = user.id_for_audit

            from core.utils import TimeUtils

            if "validity_from" not in data:
                data["validity_from"] = TimeUtils.now()
            update_or_create_report_definition(data, user)
            return None
        except Exception as exc:
            logger.exception("report.mutation.failed_to_update_report_definition")
            return [
                {
                    "message": _("report.mutation.failed_to_update_report_definition"),
                    "detail": str(exc),
                }
            ]


class Mutation(graphene.ObjectType):
    create_report_definition = CreateReportDefinitionMutation.Field()
    update_report_definition = UpdateReportDefinitionMutation.Field()
