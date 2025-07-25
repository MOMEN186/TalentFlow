from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q
from .models import Department, JobTitle, Employee
from accounts.permissions import IsAdminOrHR,IsOwnerAdminOrHR,IsAdmin,IsHR
from TalenFlow.pagination import StandardResultsSetPagination

from .serializers import (
    DepartmentSerializer,
    JobTitleSerializer,
    EmployeeListSerializer,
    EmployeeDetailSerializer,
    EmployeeCreateUpdateSerializer, EmployeeBasicSerializer
)


# Department Views
class DepartmentListCreateView(generics.ListCreateAPIView):
    """
    GET: List all departments
    POST: Create a new department
    """
    queryset = Department.objects.select_related('manager').all()
    serializer_class = DepartmentSerializer
    pagination_class = StandardResultsSetPagination
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrHR]

class DepartmentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific Department
    PUT/PATCH: Update a specific Department
    DELETE: Delete a specific Department
    """
    queryset = Department.objects.select_related('manager').all()
    serializer_class = DepartmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrHR]

# class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
#     """
#     GET: Retrieve a specific department
#     PUT/PATCH: Update a specific department
#     DELETE: Delete a specific department
#     """
#     queryset = Department.objects.select_related('manager').all()
#     serializer_class = DepartmentSerializer
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]
#
#     def destroy(self, request, *args, **kwargs):
#         """Override to prevent deletion if department has employees"""
#         department = self.get_object()
#         if department.employees.exists():
#             return Response(
#                 {'error': 'Cannot delete department with existing employees. Please reassign employees first.'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         return super().destroy(request, *args, **kwargs)


# Job Title Views
class JobTitleListCreateView(generics.ListCreateAPIView):
    """
    GET: List all job titles
    POST: Create a new job title
    """
    queryset = JobTitle.objects.all()
    serializer_class = JobTitleSerializer
    pagination_class = StandardResultsSetPagination
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrHR]


# class JobTitleDetailView(generics.RetrieveUpdateDestroyAPIView):
#     """
#     GET: Retrieve a specific job title
#     PUT/PATCH: Update a specific job title
#     DELETE: Delete a specific job title
#     """
#     queryset = JobTitle.objects.all()
#     serializer_class = JobTitleSerializer
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]
#
#     def destroy(self, request, *args, **kwargs):
#         """Override to prevent deletion if job title has employees"""
#         job_title = self.get_object()
#         if job_title.employees.exists():
#             return Response(
#                 {'error': 'Cannot delete job title with existing employees. Please reassign employees first.'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         return super().destroy(request, *args, **kwargs)

class JobTitleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific job title
    PUT/PATCH: Update a specific job title
    DELETE: Delete a specific job title
    """
    queryset = JobTitle.objects.all()
    serializer_class = JobTitleSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrHR]

# Employee Views
class EmployeeListView(generics.ListAPIView):
    """
    GET: List all employees with department and job title names
    """
    queryset = Employee.objects.select_related('department', 'job_title').all()
    serializer_class = EmployeeListSerializer
    pagination_class = StandardResultsSetPagination
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrHR]

    def get_queryset(self):
        """Add filtering capabilities"""
        queryset = super().get_queryset()
        department_id = self.request.query_params.get('department', None)
        job_title_id = self.request.query_params.get('job_title', None)
        is_active = self.request.query_params.get('active', None)

        if department_id is not None:
            queryset = queryset.filter(department_id=department_id)
        if job_title_id is not None:
            queryset = queryset.filter(job_title_id=job_title_id)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset


class EmployeeCreateView(generics.CreateAPIView):
    """
    POST: Create a new employee
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeCreateUpdateSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrHR]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Override to ensure atomic transaction"""
        return super().create(request, *args, **kwargs)


class EmployeeDetailView(generics.RetrieveAPIView):
    """
    GET: Retrieve a specific employee with full details including department and job title info
    """
    queryset = Employee.objects.select_related('department', 'job_title').all()
    serializer_class = EmployeeDetailSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrHR]


class EmployeeUpdateView(generics.UpdateAPIView):
    """
    PUT/PATCH: Update a specific employee
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeCreateUpdateSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrHR]

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """Override to ensure atomic transaction"""
        return super().update(request, *args, **kwargs)


class EmployeeDeleteView(generics.DestroyAPIView):
    """
    DELETE: Delete a specific employee
    """
    queryset = Employee.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrHR]

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """Override to handle related data cleanup"""
        employee = self.get_object()
        # Set is_active to False instead of deleting if you prefer soft delete
        # employee.is_active = False
        # employee.save()
        # return Response(status=status.HTTP_204_NO_CONTENT)
        super().destroy(request, *args, **kwargs)
        return Response(
            {"message": "Employee deleted successfully."},
            status=status.HTTP_200_OK
        )


# Custom function-based views for additional functionality
@api_view(['GET'])
@permission_classes([IsAdminOrHR])
def get_employees_by_department(request, department_id):
    """
    GET: Get all employees in a specific department
    """
    try:
        department = get_object_or_404(Department, id=department_id)
        employees = Employee.objects.filter(department=department).select_related('department', 'job_title')
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(employees, request)
        serializer = EmployeeBasicSerializer(result_page, many=True)

        return paginator.get_paginated_response({
            'department': DepartmentSerializer(department).data,
            'employees': serializer.data,
            'count': employees.count()
        })
    except Department.DoesNotExist:
        return Response(
            {'error': 'Department not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAdminOrHR])
def get_employees_by_job_title(request, job_title_id):
    """
    GET: Get all employees with a specific job title
    """
    try:
        job_title = get_object_or_404(JobTitle, id=job_title_id)
        employees = Employee.objects.filter(job_title=job_title).select_related('department', 'job_title')
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(employees, request)
        serializer = EmployeeBasicSerializer(result_page, many=True)

        return paginator.get_paginated_response({
            'job_title': JobTitleSerializer(job_title).data,
            'employees': serializer.data,
            'count': employees.count()
        })
    except JobTitle.DoesNotExist:
        return Response(
            {'error': 'Job title not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PATCH'])
@permission_classes([IsAdminOrHR])
def update_employee_status(request, employee_id):
    """
    PATCH: Update employee status (active/inactive)
    """
    try:
        employee = get_object_or_404(Employee, id=employee_id)
        status_value = request.data.get('is_active')  # Changed from 'status' to 'is_active'

        if status_value is None:
            return Response(
                {'error': 'is_active field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate boolean value
        if not isinstance(status_value, bool):
            return Response(
                {'error': 'is_active must be a boolean value'},
                status=status.HTTP_400_BAD_REQUEST
            )

        employee.is_active = status_value
        employee.save()

        serializer = EmployeeDetailSerializer(employee)
        return Response({
            'message': f'Employee status updated to {"active" if status_value else "inactive"}',
            'employee': serializer.data
        })
    except Employee.DoesNotExist:
        return Response(
            {'error': 'Employee not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAdminOrHR])
def dashboard_stats(request):
    """
    GET: Get dashboard statistics
    """
    try:
        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(is_active=True).count()
        inactive_employees = Employee.objects.filter(is_active=False).count()
        total_departments = Department.objects.count()
        total_job_titles = JobTitle.objects.count()

        # Additional stats
        departments_with_employees = Department.objects.filter(employees__isnull=False).distinct().count()
        job_titles_with_employees = JobTitle.objects.filter(employees__isnull=False).distinct().count()

        return Response({
            'total_employees': total_employees,
            'active_employees': active_employees,
            'inactive_employees': inactive_employees,
            'total_departments': total_departments,
            'total_job_titles': total_job_titles,
            'departments_with_employees': departments_with_employees,
            'job_titles_with_employees': job_titles_with_employees,
            'activity_rate': round((active_employees / total_employees * 100), 2) if total_employees > 0 else 0
        })
    except Exception as e:
        return Response(
            {'error': f'Error fetching dashboard stats: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminOrHR])
def search_employees(request):
    """
    GET: Search employees by name, phone, or national_id with pagination
    """
    query = request.query_params.get('q', '')
    if not query:
        return Response(
            {'error': 'Query parameter "q" is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    employees = Employee.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(phone__icontains=query) |
        Q(national_id__icontains=query)
    ).select_related('department', 'job_title')

    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(employees, request)
    serializer = EmployeeListSerializer(result_page, many=True)

    return paginator.get_paginated_response({
        'query': query,
        'results': serializer.data,
        'count': employees.count()
    })