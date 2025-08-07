
from django.http import HttpResponse
from rest_framework import viewsets, status
from ..models import PayRoll
from ..serializers import PayRollSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
import openpyxl

class PayRollViewSet(viewsets.ModelViewSet):
    queryset = PayRoll.objects.select_related("employee").all()
    serializer_class = PayRollSerializer

    @action(detail=False, methods=["get"], url_path="export")
    def payroll_export(self, request):
        # Fetch all employees with related data
        employees = self.get_queryset()

        # If ?excel=true, generate and return .xlsx
        if request.query_params.get("excel") in ("1", "true", "yes"):
            wb = openpyxl.Workbook(write_only=True)
            ws = wb.create_sheet(title="Payroll")

            # Header row
            ws.append([
                "ID",
                "First Name",
                "Middle Name",
                "Last Name",
                "Email",
                "Phone",
                "Department",
                "Job Title",
                "Gross Pay",
                "Tax",
                "Bonus",
                "Net Pay",
            ])

            # Data rows
            for emp in employees:
                ws.append([
                    emp.id,
                    emp.first_name,
                    emp.middle_name or "",
                    emp.last_name,
                    emp.email,
                    emp.phone,
                    emp.department.name if emp.department else "",
                    emp.job_title.name if emp.job_title else "",
                    emp.salary.gross_pay,
                    emp.salary.tax,
                    emp.salary.bonus,
                    emp.salary.net_pay,
                ])

            # Stream workbook to response
            resp = HttpResponse(
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            resp["Content-Disposition"] = 'attachment; filename="payroll.xlsx"'
            wb.save(resp)
            return resp

        # Otherwise fall back to JSON
        serializer = self.get_serializer(employees, many=True)
        return Response({"payroll": serializer.data}, status=status.HTTP_200_OK)