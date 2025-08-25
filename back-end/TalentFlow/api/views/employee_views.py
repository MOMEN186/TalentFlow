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






class EmployeeViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        
        base_queryset = Employee.objects.select_related(
            "department", "job_title"
        ).prefetch_related(
            Prefetch("payrolls", queryset=PayRoll.objects.order_by("-month", "-year"))
        )

        
        status = self.request.query_params.get('status')
        
        
        if status:
            return base_queryset.filter(status=status)
            
        
        return base_queryset.all()
    
    
    
    serializer_class = EmployeeSerializer
    
    
    permission_classes = [IsHRUser]

    
    def get_serializer_class(self):
        if self.action == 'create':
            return EmployeeCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EmployeeUpdateSerializer
        return EmployeeSerializer

    
    def retrieve(self, request, pk=None):
        employee = self.get_object()
        serializer = self.get_serializer(employee)
        return Response({"employee": serializer.data}, status=status.HTTP_200_OK)

    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.pop('email')
        password = serializer.validated_data.pop('password')

        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            full_name=f"{serializer.validated_data.get('first_name')} {serializer.validated_data.get('last_name')}"
        )
        
        employee = Employee.objects.create(
            user=user,
            **serializer.validated_data
        )

        headers = self.get_success_headers(serializer.data)
        return Response(self.get_serializer(employee).data, status=status.HTTP_201_CREATED, headers=headers)
        
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def restore(self, request, pk=None):
        try:
            employee = self.get_object()
            if employee.status == 'inactive':
                employee.status = 'active'
                employee.save(update_fields=['status'])
                return Response({'status': 'employee restored'}, status=status.HTTP_200_OK)
            return Response({'status': 'employee is already active'}, status=status.HTTP_400_BAD_REQUEST)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def payrolls(self, request, pk=None):
       
        employee = self.get_object() 
        payrolls = PayRoll.objects.filter(employee=employee)
        serializer = PayRollSerializer(payrolls, many=True)
        return Response(serializer.data)

    
    @action(detail=True, methods=['get'])
    def leave_notes(self, request, pk=None):
        
        employee = self.get_object() 
        leave_notes = employee.leave_note.all()
        serializer = LeaveNoteSerializer(leave_notes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def exit_records(self, request, pk=None):
        
        employee = self.get_object() 
        exit_records = Exit.objects.filter(employee=employee)
        serializer = ExitSerializer(exit_records, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_is_hr(self, request, pk=None):
        employee = self.get_object()
        
        
        is_hr_value = request.data.get('is_hr')

        if is_hr_value is None or not employee.user:
            return Response({'error': 'Invalid data or no user found.'}, status=400)

        try:
            hr_group, created = Group.objects.get_or_create(name='HR')

            if is_hr_value:
                employee.user.groups.add(hr_group)
                employee.user.is_staff = True
            else:
                employee.user.groups.remove(hr_group)
                employee.user.is_staff = False
            
            employee.user.save()
            return Response({'status': 'is_hr status updated successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
