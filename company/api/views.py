from accounts.models import CustomUser
from company.models import company
from .serializers import *
from rest_framework.generics import (
    CreateAPIView , ListAPIView , RetrieveAPIView,
    UpdateAPIView, DestroyAPIView
)
from rest_framework.permissions import IsAuthenticated , IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import HTTP_201_CREATED , HTTP_202_ACCEPTED
from django.db import transaction

class CompanyCreateApiView(CreateAPIView):
    serializer_class = CompanySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    
    def perform_create(self, serializer):
        serializer.save(is_active=True)
        
class CompanyUpdateAndDeleteApiView(RetrieveAPIView , UpdateAPIView, DestroyAPIView):
    serializer_class = CompanySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    queryset = company.objects.filter(is_active=True)
    lookup_field = 'id'
     
    def put(self , request , *args, **kwargs):
        company.objects.get(id=self.kwargs['id'])
        return self.update(request, *args , **kwargs)
    
    def delete(self , request , *args , **kwargs):
        instance = self.get_object()
        instance.is_active=False
        instance.save()
        return Response({"Delete Status": "Successfully Delete the Company", "Deleted Company id":instance.id}, status=HTTP_202_ACCEPTED)
    
class CompanyListApiView(ListAPIView):
    serializer_class = CompaniesListSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes =[IsAdminUser]
    
    def get_queryset(self):
        queryset = company.objects.filter(is_active=True)
        searched_data = self.request.query_params.get("q", None)
        if searched_data:
            searched_queryset = queryset.filter(company_name__icontains=searched_data)
            return searched_queryset
        else:
            return queryset
        
        
class CreateAdminApiView(CreateAPIView):
    serializer_class = AdminSerializer
    permission_classes = [IsAdminUser]
    authentication_classes =[JWTAuthentication]
    
    def perform_create(self, serializer):
        email_id = self.request.data.get('admin')
        company_id = self.request.data.get('company')  
        email_instance = CustomUser.objects.get(id=email_id)
        company_instance = company.objects.get(id=company_id)
        serializer.save(email=email_instance, company=company_instance)
    
class AdminUserUpdateAndDeleteApiView(RetrieveAPIView,UpdateAPIView, DestroyAPIView):
    serializer_class = AdminUpdateDeleteSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    queryset = AdminUser.objects.filter(is_active=True)
    lookup_field = 'id'
     
    def put(self , request , *args, **kwargs):
        AdminUser.objects.get(id=self.kwargs['id'])
        return self.update(request, *args , **kwargs)
    
    def delete(self , request , *args , **kwargs):
        instance = self.get_object()
        instance.is_active=False
        instance.save()
        return Response({"Delete Status": "Successfully Delete the Admin" , "Deleted Admin id":instance.id}, status=HTTP_202_ACCEPTED)
