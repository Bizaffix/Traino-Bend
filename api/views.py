from rest_framework.response import Response
from accounts.models import Departments, CompanyTeam
from api.serializers import DepartmentSerializer, CompanyTeamSerializer, UserCreateSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
    
class DepartmentModelViewSet(viewsets.ModelViewSet):
    queryset = Departments.objects.all()
    serializer_class = DepartmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']


    def get_queryset(self):
        return Departments.objects.filter(company_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        request.data['company'] = self.request.user.pk
        request.data['added_by'] = self.request.user.pk
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class CompanyTeamModelViewSet(viewsets.ModelViewSet):
    queryset = CompanyTeam.objects.all()
    serializer_class = CompanyTeamSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name']

    def get_queryset(self):
        return CompanyTeam.objects.filter(company_id=self.request.user.id)
    
    def create(self, request, *args, **kwargs):
        request.data['company'] = self.request.user.pk
        request.data['added_by'] = self.request.user.pk
        request.data['role'] = 'User'
        request.data['is_staff'] = 1

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.create(serializer.validated_data)
        ret = UserCreateSerializer(user)
        
        headers = self.get_success_headers(ret.data)
        return Response(ret.data, status=status.HTTP_201_CREATED, headers=headers)
    