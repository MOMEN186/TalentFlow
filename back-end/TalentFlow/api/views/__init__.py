# api/views/__init__.py
from .employee_views import EmployeeViewSet
from .leave_note_views import LeaveNoteViewSet  
from .Exit_views import ExitViewSet
__all__ = ['EmployeeViewSet', 'LeaveNoteViewSet',"ExitViewSet"]