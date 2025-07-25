from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from .models import LeaveRequest
from employees.models import Employee
from accounts.permissions import IsAdminOrHR, IsOwnerAdminOrHR
from TalenFlow.pagination import StandardResultsSetPagination
from .serializers import (
    LeaveRequestSerializer,
    LeaveRequestUpdateSerializer,
    LeaveRequestApprovalSerializer
)

# # Custom pagination class
# class StandardResultsSetPagination(PageNumberPagination):
#     page_size = 10  # Default page size
#     page_size_query_param = 'page_size'  # Allow client to override page size
#     max_page_size = 100  # Maximum page size limit
#     page_query_param = 'page'
# 
#     def get_paginated_response(self, data):
#         return Response({
#             'count': self.page.paginator.count,
#             'next': self.get_next_link(),
#             'previous': self.get_previous_link(),
#             'total_pages': self.page.paginator.num_pages,
#             'current_page': self.page.number,
#             'page_size': self.page_size,
#             'results': data
#         })

# 1. API to list all leave requests (Admin and HR only)
class AllLeaveRequestsListView(generics.ListAPIView):
    """
    List all leave requests - Admin and HR only
    """
    queryset = LeaveRequest.objects.all().select_related('employee', 'approved_by')
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAdminOrHR]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return LeaveRequest.objects.all().select_related(
            'employee__department',
            'employee__job_title',
            'approved_by'
        ).order_by('-request_date')


# 2. API for employees to see their own leave requests
class MyLeaveRequestsListView(generics.ListAPIView):
    """
    List current user's leave requests
    """
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            employee = Employee.objects.get(user=self.request.user)
            return LeaveRequest.objects.filter(employee=employee).select_related(
                'employee__department',
                'employee__job_title',
                'approved_by'
            ).order_by('-request_date')
        except Employee.DoesNotExist:
            return LeaveRequest.objects.none()


# 3. API to get approved leave requests (Admin and HR only)
class ApprovedLeaveRequestsListView(generics.ListAPIView):
    """
    List all approved leave requests - Admin and HR only
    """
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAdminOrHR]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return LeaveRequest.objects.filter(status='Approved').select_related(
            'employee__department',
            'employee__job_title',
            'approved_by'
        ).order_by('-request_date')


# 4. API to get rejected leave requests (Admin and HR only)
class RejectedLeaveRequestsListView(generics.ListAPIView):
    """
    List all rejected leave requests - Admin and HR only
    """
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAdminOrHR]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return LeaveRequest.objects.filter(status='Rejected').select_related(
            'employee__department',
            'employee__job_title',
            'approved_by'
        ).order_by('-request_date')


# 5. API to get pending leave requests (Admin and HR only)
class PendingLeaveRequestsListView(generics.ListAPIView):
    """
    List all pending leave requests - Admin and HR only
    """
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAdminOrHR]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return LeaveRequest.objects.filter(status='Pending').select_related(
            'employee__department',
            'employee__job_title',
            'approved_by'
        ).order_by('-request_date')


# 6. API to create new leave request
class CreateLeaveRequestView(generics.CreateAPIView):
    """
    Create a new leave request (max 21 days)
    """
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]


# 7. API to delete leave request
@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_leave_request(request, pk):
    """
    Delete a leave request.
    Employee can delete their own request.
    Admin and HR can delete any request.
    """
    leave_request = get_object_or_404(LeaveRequest, pk=pk)

    # Check permissions
    is_admin_or_hr = (
            request.user.is_superuser or
            getattr(request.user, 'role', None) == 'HR'
    )

    is_owner = False
    try:
        employee = Employee.objects.get(user=request.user)
        is_owner = leave_request.employee == employee
    except Employee.DoesNotExist:
        pass

    if not (is_admin_or_hr or is_owner):
        return Response(
            {'error': 'You do not have permission to delete this leave request.'},
            status=status.HTTP_403_FORBIDDEN
        )

    leave_request.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# 8. API to approve or reject leave request
@api_view(['PATCH'])
@permission_classes([IsAdminOrHR])
def approve_reject_leave_request(request, pk):
    """
    Approve or reject a leave request.
    When approved, decreases employee's annual_leave_balance.
    Admin and HR only.
    """
    leave_request = get_object_or_404(LeaveRequest, pk=pk)

    # Check if request is still pending
    if leave_request.status != 'Pending':
        return Response(
            {'error': f'Leave request is already {leave_request.status.lower()}.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = LeaveRequestApprovalSerializer(
        leave_request,
        data=request.data,
        context={'request': request},
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(
            LeaveRequestSerializer(leave_request).data,
            status=status.HTTP_200_OK
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 9. API to update leave request
class UpdateLeaveRequestView(generics.UpdateAPIView):
    """
    Update a leave request.
    Employee can update their own request only.
    Admin and HR can update any request.
    """
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerAdminOrHR]

    def get_object(self):
        obj = super().get_object()

        # Check if request is still pending (only pending requests can be updated)
        if obj.status != 'Pending':
            from rest_framework.exceptions import ValidationError
            raise ValidationError(f'Cannot update {obj.status.lower()} leave request.')

        return obj


# 10. API to get single leave request details
class LeaveRequestDetailView(generics.RetrieveAPIView):
    """
    Get details of a specific leave request.
    Employee can view their own request.
    Admin and HR can view any request.
    """
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerAdminOrHR]