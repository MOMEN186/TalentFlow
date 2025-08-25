# api/views/__init__.py
from .employee_views import EmployeeViewSet
from .leave_note_views import LeaveNoteViewSet  
from .Exit_views import ExitViewSet
from .department_views import DepartmentViewSet
from .jobTitle_views import JobTitleViewSet

__all__ = ['EmployeeViewSet', 'LeaveNoteViewSet',"ExitViewSet","DepartmentViewSet","JobTitleViewSet"]