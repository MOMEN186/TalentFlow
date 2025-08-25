from rest_framework import viewsets
from ..models import JobTitle
from ..serializers import JobTitleSerializer

class JobTitleViewSet(viewsets.ModelViewSet):
    queryset = JobTitle.objects.all()
    serializer_class = JobTitleSerializer