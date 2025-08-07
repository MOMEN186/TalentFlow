from django.http import HttpResponse
from ..serializers import  LeaveNoteSerializer
from rest_framework import viewsets, status
from ..models import  LeaveNote
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.timezone import now

import openpyxl


class LeaveNoteViewSet(viewsets.ModelViewSet):
    queryset = LeaveNote.objects.all().select_related("employee")
    serializer_class = LeaveNoteSerializer
    
    @action(detail=False, methods=["get"], url_path="leave_notes")
    def leave_notes(self, request):
        query = LeaveNote.objects.select_related("employee").filter(
            date__gt=now().date()
        )
        serializer = LeaveNoteSerializer(query, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="export")
    def leave_notes_export(self, request):
        """
        GET /api/employees/leave_notes/export/
        • ?excel=true → streams an .xlsx file of future leave notes
        • otherwise   → returns JSON of future leave notes
        """
        # 1) only future notes
        future_notes = LeaveNote.objects.select_related("employee").filter(
            date__gt=now().date()
        )

        # 2) Excel branch?
        if request.query_params.get("excel") in ("1", "true", "yes"):
            wb = openpyxl.Workbook(write_only=True)
            ws = wb.create_sheet(title="LeaveNotes")
            ws.append(["ID", "Employee", "From", "To", "Reason"])
            for note in future_notes:
                full_name = " ".join(
                    filter(
                        None,
                        [
                            note.employee.first_name,
                            note.employee.middle_name,
                            note.employee.last_name,
                        ],
                    )
                )
                ws.append(
                    [
                        note.id,
                        full_name,
                        note.date.strftime("%Y-%m-%d"),
                        note.return_date.strftime("%Y-%m-%d"),
                        note.description,
                    ]
                )
            resp = HttpResponse(
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            resp["Content-Disposition"] = 'attachment; filename="leave_notes.xlsx"'
            wb.save(resp)
            return resp

        # 3) JSON branch
        serializer = LeaveNoteSerializer(future_notes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

