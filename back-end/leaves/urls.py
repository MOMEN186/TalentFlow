from django.urls import path
from . import views


urlpatterns = [
    # List views for admin/HR
    path('leaves/', views.AllLeaveRequestsListView.as_view(), name='all-leave-requests'),
    path('leaves/approved/', views.ApprovedLeaveRequestsListView.as_view(), name='approved-leave-requests'),
    path('leaves/rejected/', views.RejectedLeaveRequestsListView.as_view(), name='rejected-leave-requests'),
    path('leaves/pending/', views.PendingLeaveRequestsListView.as_view(), name='pending-leave-requests'),

    # Employee's own requests
    path('leaves/my-requests/', views.MyLeaveRequestsListView.as_view(), name='my-leave-requests'),

    # CRUD operations
    path('leaves/create/', views.CreateLeaveRequestView.as_view(), name='create-leave-request'),
    path('leaves/<int:pk>/', views.LeaveRequestDetailView.as_view(), name='leave-request-detail'),
    path('leaves/<int:pk>/update/', views.UpdateLeaveRequestView.as_view(), name='update-leave-request'),
    path('leaves/<int:pk>/delete/', views.delete_leave_request, name='delete-leave-request'),

    # Approval/Rejection
    path('leaves/<int:pk>/approve-reject/', views.approve_reject_leave_request, name='approve-reject-leave-request'),
]