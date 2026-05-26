from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from records.models import EmissionRecord, AuditLog
from .serializers import EmissionRecordSerializer, AuditLogSerializer


class EmissionRecordViewSet(viewsets.ModelViewSet):
    serializer_class = EmissionRecordSerializer

    def get_queryset(self):
        qs = EmissionRecord.objects.all().order_by('-created_at')
        scope = self.request.query_params.get('scope')
        review_status = self.request.query_params.get('status')
        flagged = self.request.query_params.get('flagged')
        source_type = self.request.query_params.get('source_type')

        if scope:
            qs = qs.filter(scope=scope)
        if review_status:
            qs = qs.filter(review_status=review_status)
        if flagged == 'true':
            qs = qs.filter(review_status='FLAGGED')
        if source_type:
            qs = qs.filter(source__source_type=source_type)
        return qs

    def _update_status(self, request, new_status, action_name):
        record = self.get_object()
        old_status = record.review_status
        record.review_status = new_status
        record.reviewed_by = request.user
        record.reviewed_at = timezone.now()
        record.review_note = request.data.get('note', '')

        if new_status == 'FLAGGED':
            record.has_warning = True
            record.warning_reason = record.review_note or 'Manually flagged by analyst'
        elif new_status in ('APPROVED', 'REJECTED', 'LOCKED'):
            record.has_warning = False
            record.warning_reason = ''

        record.save()
        AuditLog.objects.create(
            record=record,
            actor=request.user,
            action=action_name,
            before={'review_status': old_status},
            after={'review_status': new_status},
            note=record.review_note,
        )
        return Response(EmissionRecordSerializer(record).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        return self._update_status(request, 'APPROVED', 'APPROVED')

    @action(detail=True, methods=['post'])
    def flag(self, request, pk=None):
        return self._update_status(request, 'FLAGGED', 'FLAGGED')

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        return self._update_status(request, 'REJECTED', 'REJECTED')

    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        return self._update_status(request, 'LOCKED', 'LOCKED')

    @action(detail=True, methods=['get'])
    def audit_trail(self, request, pk=None):
        record = self.get_object()
        logs = AuditLog.objects.filter(record=record).order_by('timestamp')
        return Response(AuditLogSerializer(logs, many=True).data)

    @action(detail=False, methods=['post'])
    def bulk_approve(self, request):
        ids = request.data.get('ids', [])
        EmissionRecord.objects.filter(id__in=ids).update(
            review_status='APPROVED',
            has_warning=False,
            warning_reason='',
            reviewed_at=timezone.now()
        )
        return Response({'approved': len(ids)})


class DashboardSummaryView(APIView):
    def get(self, request):
        from django.db.models import Sum
        qs = EmissionRecord.objects.all()
        data = {
            'scope1_co2e': float(qs.filter(scope=1).aggregate(t=Sum('co2e_kg'))['t'] or 0),
            'scope2_co2e': float(qs.filter(scope=2).aggregate(t=Sum('co2e_kg'))['t'] or 0),
            'scope3_co2e': float(qs.filter(scope=3).aggregate(t=Sum('co2e_kg'))['t'] or 0),
            'pending':  qs.filter(review_status='PENDING').count(),
            'flagged':  qs.filter(review_status='FLAGGED').count(),
            'approved': qs.filter(review_status='APPROVED').count(),
            'total':    qs.count(),
        }
        return Response(data)