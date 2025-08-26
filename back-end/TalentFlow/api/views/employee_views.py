import time
import logging
from contextlib import contextmanager
from functools import wraps
from django.db import connection
from django.conf import settings

from ..models import Employee, LeaveNote, Exit
from hr.models import PayRoll
from rest_framework import viewsets, status
from rest_framework.response import Response
from ..serializers import (EmployeeSerializer, EmployeeCreateSerializer, EmployeeUpdateSerializer, LeaveNoteSerializer, ExitSerializer)
from hr.serializers import PayRollSerializer
from TalentFlow.accounts.models import CustomUser
from TalentFlow.accounts.permissions import IsHRUser
from django.db.models import Prefetch
from django.db import transaction
from rest_framework.decorators import action
from django.contrib.auth.models import Group

# Configure logger
logger = logging.getLogger(__name__)

@contextmanager
def timer(operation_name, logger_instance=None):
    """Context manager to time operations and log results"""
    start_time = time.time()
    start_queries = len(connection.queries) if settings.DEBUG else 0
    
    try:
        yield
    finally:
        end_time = time.time()
        end_queries = len(connection.queries) if settings.DEBUG else 0
        
        duration = (end_time - start_time) * 1000  # Convert to milliseconds
        query_count = end_queries - start_queries
        
        log_msg = f"{operation_name} - Duration: {duration:.2f}ms"
        if settings.DEBUG:
            log_msg += f" - DB Queries: {query_count}"
            
        if logger_instance:
            logger_instance.info(log_msg)
        else:
            logger.info(log_msg)

def log_method_timing(method_name=None):
    """Decorator to log method execution time"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            operation = method_name or f"{self.__class__.__name__}.{func.__name__}"
            
            with timer(f"[{operation}] Total execution", logger):
                result = func(self, *args, **kwargs)
            
            return result
        return wrapper
    return decorator

class EmployeeViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        with timer("[EmployeeViewSet.get_queryset] Building queryset", logger):
            base_queryset = Employee.objects.select_related(
                "department", "job_title"
            ).prefetch_related(
                Prefetch("payrolls", queryset=PayRoll.objects.order_by("-month", "-year"))
            )

            status_param = self.request.query_params.get('status')
            
            if status_param:
                with timer(f"[EmployeeViewSet.get_queryset] Filtering by status: {status_param}", logger):
                    return base_queryset.filter(status=status_param)
            
            return base_queryset.all()
    
    serializer_class = EmployeeSerializer
    permission_classes = [IsHRUser]

    def get_serializer_class(self):
        if self.action == 'create':
            return EmployeeCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EmployeeUpdateSerializer
        return EmployeeSerializer

    @log_method_timing("Employee Retrieve")
    def retrieve(self, request, pk=None):
        with timer("[EmployeeViewSet.retrieve] Getting employee object", logger):
            employee = self.get_object()
        
        with timer("[EmployeeViewSet.retrieve] Serializing employee data", logger):
            serializer = self.get_serializer(employee)
            serialized_data = serializer.data
        
        return Response({"employee": serialized_data}, status=status.HTTP_200_OK)

    @log_method_timing("Employee Create")
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        with timer("[EmployeeViewSet.create] Validating serializer data", logger):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

        with timer("[EmployeeViewSet.create] Extracting user credentials", logger):
            email = serializer.validated_data.pop('email')
            password = serializer.validated_data.pop('password')

        with timer("[EmployeeViewSet.create] Creating CustomUser", logger):
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                full_name=f"{serializer.validated_data.get('first_name')} {serializer.validated_data.get('last_name')}"
            )
        
        with timer("[EmployeeViewSet.create] Creating Employee record", logger):
            employee = Employee.objects.create(
                user=user,
                **serializer.validated_data
            )

        with timer("[EmployeeViewSet.create] Serializing response data", logger):
            response_serializer = self.get_serializer(employee)
            response_data = response_serializer.data

        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
        
    @log_method_timing("Employee Update")
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        
        with timer("[EmployeeViewSet.update] Getting employee instance", logger):
            instance = self.get_object()
        
        with timer("[EmployeeViewSet.update] Validating and saving data", logger):
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        
        return Response(serializer.data)

    @log_method_timing("Employee Restore")
    @action(detail=True, methods=['patch'])
    def restore(self, request, pk=None):
        try:
            with timer("[EmployeeViewSet.restore] Getting and updating employee", logger):
                employee = self.get_object()
                if employee.status == 'inactive':
                    employee.status = 'active'
                    employee.save(update_fields=['status'])
                    return Response({'status': 'employee restored'}, status=status.HTTP_200_OK)
                return Response({'status': 'employee is already active'}, status=status.HTTP_400_BAD_REQUEST)
        except Employee.DoesNotExist:
            logger.warning(f"[EmployeeViewSet.restore] Employee with pk={pk} not found")
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @log_method_timing("Employee Payrolls")
    @action(detail=True, methods=['get'])
    def payrolls(self, request, pk=None):
        with timer("[EmployeeViewSet.payrolls] Getting employee", logger):
            employee = self.get_object()
        
        with timer("[EmployeeViewSet.payrolls] Querying payroll records", logger):
            payrolls = PayRoll.objects.filter(employee=employee)
        
        with timer("[EmployeeViewSet.payrolls] Serializing payroll data", logger):
            serializer = PayRollSerializer(payrolls, many=True)
            serialized_data = serializer.data
        
        return Response(serialized_data)

    @log_method_timing("Employee Leave Notes")
    @action(detail=True, methods=['get'])
    def leave_notes(self, request, pk=None):
        with timer("[EmployeeViewSet.leave_notes] Getting employee", logger):
            employee = self.get_object()
        
        with timer("[EmployeeViewSet.leave_notes] Getting leave notes", logger):
            leave_notes = employee.leave_note.all()
        
        with timer("[EmployeeViewSet.leave_notes] Serializing leave notes", logger):
            serializer = LeaveNoteSerializer(leave_notes, many=True)
            serialized_data = serializer.data
        
        return Response(serialized_data)
    
    @log_method_timing("Employee Exit Records")
    @action(detail=True, methods=['get'])
    def exit_records(self, request, pk=None):
        with timer("[EmployeeViewSet.exit_records] Getting employee", logger):
            employee = self.get_object()
        
        with timer("[EmployeeViewSet.exit_records] Querying exit records", logger):
            exit_records = Exit.objects.filter(employee=employee)
        
        with timer("[EmployeeViewSet.exit_records] Serializing exit records", logger):
            serializer = ExitSerializer(exit_records, many=True)
            serialized_data = serializer.data
        
        return Response(serialized_data)
    
    @log_method_timing("Employee Update HR Status")
    @action(detail=True, methods=['patch'])
    def update_is_hr(self, request, pk=None):
        with timer("[EmployeeViewSet.update_is_hr] Getting employee", logger):
            employee = self.get_object()
        
        is_hr_value = request.data.get('is_hr')

        if is_hr_value is None or not employee.user:
            logger.warning(f"[EmployeeViewSet.update_is_hr] Invalid data or no user found for employee {pk}")
            return Response({'error': 'Invalid data or no user found.'}, status=400)

        try:
            with timer("[EmployeeViewSet.update_is_hr] Updating HR group membership", logger):
                hr_group, created = Group.objects.get_or_create(name='HR')

                if is_hr_value:
                    employee.user.groups.add(hr_group)
                    employee.user.is_staff = True
                else:
                    employee.user.groups.remove(hr_group)
                    employee.user.is_staff = False
                
                employee.user.save()
            
            logger.info(f"[EmployeeViewSet.update_is_hr] Successfully updated HR status for employee {pk} to {is_hr_value}")
            return Response({'status': 'is_hr status updated successfully'})
        except Exception as e:
            logger.error(f"[EmployeeViewSet.update_is_hr] Error updating HR status for employee {pk}: {str(e)}")
            return Response({'error': str(e)}, status=500)

    def list(self, request, *args, **kwargs):
        """Override list method to add timing"""
        with timer("[EmployeeViewSet.list] Getting queryset", logger):
            queryset = self.filter_queryset(self.get_queryset())

        with timer("[EmployeeViewSet.list] Applying pagination", logger):
            page = self.paginate_queryset(queryset)
            
        if page is not None:
            with timer("[EmployeeViewSet.list] Serializing paginated data", logger):
                serializer = self.get_serializer(page, many=True)
                paginated_response = self.get_paginated_response(serializer.data)
            return paginated_response

        with timer("[EmployeeViewSet.list] Serializing all data", logger):
            serializer = self.get_serializer(queryset, many=True)
            serialized_data = serializer.data

        return Response(serialized_data)