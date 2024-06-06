from accounts.models import CustomUser
from company.models import company
from .serializers import *
from rest_framework.generics import (
    CreateAPIView , ListAPIView , RetrieveAPIView,
    UpdateAPIView, DestroyAPIView
)
from rest_framework.views import APIView
from .permissions import IsAdminUserOrReadOnly, IsAdminListOrReadOnly
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
            company_name = company.objects.filter(name=name, is_active=True)
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
        
        # Marked company as inactive
        instance.is_active = False
        instance.save()

        # Marked all admin users as inactive
        instance.company.all().update(is_active=False)

        # Marked all departments and their related documents as inactive
        departments = instance.department_company.all()
        for department in departments:
            department.is_active = False
            department.save()

            # Marked all department documents as inactive
            documents = department.document_departments.all()
            for document in documents:
                document.is_active = False
                document.save()

                # Marked all summaries, keypoints, and quizzes related to the document as inactive
                document.summary_document.all().delete()
                document.documentkeypoints_set.all().delete()
                document.documentquiz_set.all().delete()

        # Marked all company teams as inactive
        instance.company_teams.all().update(is_active=False)

        return Response({"Delete Status": "Successfully deleted the Company", "id": instance.id}, status=HTTP_202_ACCEPTED)

from rest_framework.filters import SearchFilter, OrderingFilter

class CompanyListApiView(ListAPIView):
    serializer_class = CompaniesListSerializer
    authentication_classes = [JWTAuthentication]
    filter_backends = [SearchFilter, OrderingFilter]
    permission_classes =[IsAdminUserOrReadOnly]
    search_fields = ['id','name', 'company_id', 'logo', 'phone', 'country', 'address', 'city', 'fax', 'state_or_province', 'zip_code', 'website_url']
    ordering_fields = ['id','name', 'company_id', 'logo', 'phone', 'country', 'address', 'city', 'fax', 'state_or_province', 'zip_code', 'website_url']
    ordering = ['id','name', 'company_id', 'logo', 'phone', 'country', 'address', 'city', 'fax', 'state_or_province', 'zip_code', 'website_url']  # Default ordering (A-Z by company_name)
    
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
    permission_classes = [IsAdminListOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','admin__first_name','admin__last_name', 'admin__email' , 'admin__role', 'admin__created_at', 'admin__updated_at', 'company__name']
    ordering_fields = ['id','admin__first_name','admin__last_name', 'admin__email' , 'admin__role', 'admin__created_at', 'admin__updated_at', 'company__name']
    ordering = ['id','admin__first_name','admin__last_name', 'admin__email' , 'admin__role', 'admin__created_at', 'admin__updated_at', 'company__name']  # Default ordering (A-Z by company_name)
    queryset = AdminUser.objects.filter(is_active=True)

    def get_queryset(self):
        """
        Optionally restricts the returned administrators to a given company,
        by filtering against a `company_id` query parameter in the URL.
        """
        if self.request.user.role == 'Super Admin' or self.request.user.role == 'Admin': 
            company_id = self.request.query_params.get('company_id', None)
            if self.request.user.role == 'Admin':
                admin = AdminUser.objects.get(admin=self.request.user)
                if admin.is_active == True:
                    if str(company_id) == str(admin.company.id):
                        queryset = AdminUser.objects.filter(is_active=True)
                        if company_id:
                            queryset = queryset.filter(company__id=company_id)
                        return queryset
                    else:
                        return Response({"Unauthorized": "You are not allowed to see the admins of this company"}, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    raise serializers.ValidationError({"Unauthorized": "You are blocked or deleted"})
            else:
                queryset = AdminUser.objects.filter(is_active=True)
                company_id = self.request.query_params.get('company_id', None)
                if company_id is not None:
                    queryset = queryset.filter(company__id=company_id)
                return queryset    
        else:
            raise serializers.ValidationError({"Access Denied":"You are not allowed for this request"})
    
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