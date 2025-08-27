from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.timezone import now

import openpyxl

from ..serializers import LeaveNoteSerializer
from ..models import LeaveNote, LeaveNoteStatus
from django.db.models import Q


class LeaveNoteViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveNoteSerializer

    def get_queryset(self):
        queryset = LeaveNote.objects.all().select_related("employee")
        
        status_param = self.request.query_params.get('status')
        
        if status_param and status_param in LeaveNoteStatus.values:
            queryset = queryset.filter(Q(status=status_param))
        
        return queryset.order_by('-date')
    
    @action(detail=False, methods=["get"], url_path="export")
    def leave_notes_export(self, request):
        
        future_notes = self.get_queryset().filter(date__gt=now().date()).order_by('date')
        
        
        wb = openpyxl.Workbook(write_only=True)
        ws = wb.create_sheet(title="LeaveNotes")
        ws.append(["ID", "Employee", "From", "To", "Reason", "Status"])
        for note in future_notes:
            full_name = " ".join(filter(None, [note.employee.first_name, note.employee.middle_name, note.employee.last_name]))
            ws.append([note.id, full_name, note.date.strftime("%Y-%m-%d"), note.return_date.strftime("%Y-%m-%d"), note.description, note.status])

        resp = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        resp["Content-Disposition"] = 'attachment; filename="leave_notes.xlsx"'
        wb.save(resp)
        return resp