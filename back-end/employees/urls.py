from django.urls import path
from . import views

urlpatterns = [
    # Department URLs
    path('departments/', views.DepartmentListCreateView.as_view(), name='department-list-create'),
    # path('departments/<int:pk>/', views.DepartmentDetailView.as_view(), name='department-detail'),
    path('departments/<int:pk>/', views.DepartmentRetrieveUpdateDestroyView.as_view(), name='department-detail'),
    path('departments/<int:department_id>/employees/', views.get_employees_by_department, name='department-employees'),

    # Job Title URLs
    path('job-titles/', views.JobTitleListCreateView.as_view(), name='jobtitle-list-create'),
    # path('job-titles/<int:pk>/', views.JobTitleDetailView.as_view(), name='jobtitle-detail'),
    path('job-titles/<int:pk>/', views.JobTitleRetrieveUpdateDestroyView.as_view(), name='jobtitle-detail'),
    path('job-titles/<int:job_title_id>/employees/', views.get_employees_by_job_title, name='jobtitle-employees'),

    # Employee URLs
    path('employees/', views.EmployeeListView.as_view(), name='employee-list'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee-create'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/<int:pk>/update/', views.EmployeeUpdateView.as_view(), name='employee-update'),
    path('employees/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee-delete'),
    path('employees/<int:employee_id>/status/', views.update_employee_status, name='employee-status-update'),

    # Search by first name: /employees/search/?q=John
    # Search by last name: /employees/search/?q=Smith
    # Search by phone: /employees/search/?q=01234567890
    # Search by national ID: /employees/search/?q=12345678901234
    path('employees/search/', views.search_employees, name='search-employees'),

    # Dashboard/Stats
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
]