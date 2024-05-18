from accounts.models import CustomUser
from company.models import company
from .serializers import *
from rest_framework.generics import (
    CreateAPIView , ListAPIView , RetrieveAPIView,
    UpdateAPIView, DestroyAPIView
)
from rest_framework.views import APIView
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
        name = self.request.data.get('name')
        try:
            company_name = company.objects.get(name=name)
            if company_name:
                raise serializers.ValidationError(
                    {"Company Exists": f"Company with this name {name} already exists"})
        except company.DoesNotExist:
            # User does not exist, so continue with user creation
            pass
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
        return Response({"Delete Status": "Successfully deleted the Company", "id": instance.id}, status=HTTP_202_ACCEPTED)

from rest_framework.filters import SearchFilter, OrderingFilter

class CompanyListApiView(ListAPIView):
    serializer_class = CompaniesListSerializer
    authentication_classes = [JWTAuthentication]
    filter_backends = [SearchFilter, OrderingFilter]
    permission_classes =[IsAdminUserOrReadOnly]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']  # Default ordering (A-Z by company_name)
    
    def get_queryset(self):
        queryset = company.objects.filter(is_active=True)
        searched_data = self.request.query_params.get("company_name", None)
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
        email_id = self.request.data.get('admin')
        company_id = self.request.data.get('company')  
        if email_id is None:
            raise serializers.ValidationError("Admin field is required.")

        email_instance = CustomUser.objects.filter(id=email_id).first()
        if email_instance is None:
            raise serializers.ValidationError("Invalid admin specified.")

        company_instance = company.objects.filter(id=company_id).first()
        if company_instance is None:
            raise serializers.ValidationError("Invalid company specified.")

        serializer.save(admin=email_instance, company=company_instance)

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
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['admin__first_name']
    ordering_fields = ['admin__first_name']
    ordering = ['admin__first_name']  # Default ordering (A-Z by company_name)
    queryset = AdminUser.objects.filter(is_active=True)

    def get_queryset(self):
        """
        Optionally restricts the returned administrators to a given company,
        by filtering against a `company_id` query parameter in the URL.
        """
        queryset = AdminUser.objects.filter(is_active=True)
        company_id = self.request.query_params.get('company_id', None)
        if company_id is not None:
            queryset = queryset.filter(company__id=company_id)
        return queryset
    
class BulkAdminDeleteAPIView(APIView):
    permission_classes = [IsAdminUserOrReadOnly]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request, format=None):
        # Extract the list of admin IDs from the request data
        admin_ids = request.data.get('admin_ids', [])

        # Validate that admin IDs are provided
        if not admin_ids:
            return Response({"message": "Admin IDs are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Update the is_active field of each admin
        for admin_id in admin_ids:
            try:
                admin = AdminUser.objects.get(id=admin_id)
                admin.is_active = False
                admin.save()
            except AdminUser.DoesNotExist:
                return Response({"message": f"Admin with ID {admin_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Admins Deleted successfully"}, status=status.HTTP_200_OK)