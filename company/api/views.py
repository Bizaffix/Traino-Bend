from accounts.models import CustomUser
from company.models import company
from .serializers import *
from rest_framework.generics import (
    CreateAPIView , ListAPIView , RetrieveAPIView,
    UpdateAPIView, DestroyAPIView
)
from .permissions import IsAdminUserOrReadOnly
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
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = company.objects.filter(is_active=True)
    lookup_field = 'id'
     
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({"Delete Status": "Successfully deleted the Company", "Deleted Company id": instance.id}, status=HTTP_202_ACCEPTED)
class CompanyListApiView(ListAPIView):
    serializer_class = CompaniesListSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes =[IsAdminUserOrReadOnly]
    
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
    permission_classes = [IsAdminUserOrReadOnly]
    authentication_classes =[JWTAuthentication]
    
    def perform_create(self, serializer):
        email_id = self.request.data.get('email')
        company_id = self.request.data.get('company')  
        if email_id is None:
            raise serializers.ValidationError("Admin field is required.")

        email_instance = CustomUser.objects.filter(id=email_id).first()
        if email_instance is None:
            raise serializers.ValidationError("Invalid admin specified.")

        company_instance = company.objects.filter(id=company_id).first()
        if company_instance is None:
            raise serializers.ValidationError("Invalid company specified.")

        serializer.save(email=email_instance, company=company_instance)

class AdminUserUpdateAndDeleteApiView(RetrieveAPIView,UpdateAPIView, DestroyAPIView):
    serializer_class = AdminUpdateDeleteSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = AdminUser.objects.filter(is_active=True)
    lookup_field = 'id'
     
    def put(self , request , *args, **kwargs):
        AdminUser.objects.get(id=self.kwargs['id'])
        return self.update(request, *args , **kwargs)
    
    def delete(self , request , *args , **kwargs):
        instance = self.get_object()
        instance.is_active=False
        instance.save()
        return Response({"status": "Successfully Delete the Admin" , "id":instance.id}, status=HTTP_202_ACCEPTED)
class AdminListApiView(ListAPIView):
    serializer_class = AdminUpdateDeleteSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    queryset = AdminUser.objects.filter(is_active=True)
