from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from records.models import Tenant, DataSource, EmissionRecord
from .parsers import parse_sap, parse_utility, parse_travel

PARSER_MAP = {
    'SAP_FLAT': parse_sap,
    'UTILITY_CSV': parse_utility,
    'TRAVEL_CSV': parse_travel,
}


class UploadView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        source_type = request.data.get('source_type')
        tenant_id = request.data.get('tenant_id', 1)

        if not file or not source_type:
            return Response(
                {'error': 'file and source_type are required'},
                status=status.HTTP_400_BAD_REQUEST)

        if source_type not in PARSER_MAP:
            return Response(
                {'error': f'Unknown source_type: {source_type}'},
                status=status.HTTP_400_BAD_REQUEST)

        tenant = Tenant.objects.get(id=tenant_id)
        datasource = DataSource.objects.create(
            tenant=tenant,
            source_type=source_type,
            file_name=file.name,
            uploaded_by=request.user,
            status='PROCESSING',
        )

        parser = PARSER_MAP[source_type]
        parsed_records, errors = parser(file)

        emission_records = [
            EmissionRecord(
                tenant=tenant,
                source=datasource,
                **rec
            )
            for rec in parsed_records
        ]
        EmissionRecord.objects.bulk_create(emission_records)

        datasource.row_count = len(emission_records)
        datasource.error_count = len(errors)
        datasource.errors_json = errors
        datasource.status = 'DONE'
        datasource.save()

        return Response({
            'datasource_id': datasource.id,
            'rows_imported': len(emission_records),
            'errors': errors,
        })