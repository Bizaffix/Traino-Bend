from teams.models import CompaniesTeam
from rest_framework.generics import (
    CreateAPIView, UpdateAPIView , RetrieveAPIView , DestroyAPIView, ListAPIView
)
from .serializers import CompaniesTeamSerializer , CompaniesTeamDetailsSerializers, CompaniesTeamDetailFullSerializers
from .permissions import IsAdminUserOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication 
from .permissions import IsAdminUserOrReadOnly, IsActiveAdminPermission , IsActiveAdminUsersPermission
from rest_framework import serializers
from company.models import AdminUser
from accounts.models import CustomUser

class AddMembersApiView(CreateAPIView):
    serializer_class = CompaniesTeamSerializer
    permission_classes = [IsAdminUserOrReadOnly, IsActiveAdminPermission]
    authentication_classes = [JWTAuthentication]
    
    def perform_create(self , serializer):
        serializer.save(is_active=True)

class MembersUpdateDestroyApiView(RetrieveAPIView , UpdateAPIView, DestroyAPIView):
    serializer_class = CompaniesTeamDetailFullSerializers
    permission_classes = [IsAdminUserOrReadOnly]
    authentication_classes = [JWTAuthentication]
    queryset = CompaniesTeam.objects.filter(is_active=True)
    lookup_field = 'id'
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data

        # Handle both full and partial updates
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        kwargs['partial'] = False
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def delete(self , request , *args , **kwargs):
        instance = self.get_object()
        instance.is_active=False
        instance.save()
        user = CustomUser.objects.get(email=instance.members.email)
        user.delete()
        return Response({"Delete Status": "Successfully Removed the User" , "id":instance.id}, status=status.HTTP_202_ACCEPTED)

from rest_framework.filters import SearchFilter, OrderingFilter
    
class MembersListApiView(ListAPIView):
    serializer_class = CompaniesTeamDetailsSerializers
    permission_classes = [IsAdminUserOrReadOnly, IsActiveAdminPermission]
    authentication_classes = [JWTAuthentication]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id', 'members__first_name', 'members__last_name', 'members__email', 'members__phone', 'members__role']
    ordering_fields = ['id', 'members__first_name', 'members__last_name', 'members__email', 'members__phone', 'members__role']
    ordering = ['id', 'members__first_name', 'members__last_name', 'members__email', 'members__phone', 'members__role']
    queryset = CompaniesTeam.objects.filter(is_active=True)

    def get_queryset(self):
        user = self.request.user

        if user.role == "Admin":
            try:
                admin_user = AdminUser.objects.get(admin=user, is_active=True)
                company = admin_user.company
            except AdminUser.DoesNotExist:
                raise serializers.ValidationError({"Unauthorized": "You are blocked or deleted"})

            queryset = CompaniesTeam.objects.filter(company=company, is_active=True)

            requested_company_id = self.request.query_params.get('company_id')
            if requested_company_id:
                if str(requested_company_id) != str(company.id):
                    raise serializers.ValidationError({"Access Denied": "You are not allowed to view users of another company."})
                else:
                    queryset = queryset.filter(company_id=requested_company_id)

            requested_department_id = self.request.query_params.get('department_id')
            if requested_department_id:
                queryset = queryset.filter(departments__id=requested_department_id)

            requested_document_id = self.request.query_params.get('document_id')
            if requested_document_id:
                queryset = queryset.filter(departments__document_departments__id=requested_document_id)

            return queryset

        elif user.role == "Super Admin":
            queryset = self.queryset

            requested_company_id = self.request.query_params.get('company_id', None)
            if requested_company_id:
                queryset = queryset.filter(company_id=requested_company_id)

            requested_department_id = self.request.query_params.get('department_id' , None)
            if requested_department_id:
                queryset = queryset.filter(departments__id=requested_department_id)

            requested_document_id = self.request.query_params.get('document_id' ,None)
            if requested_document_id:
                queryset = queryset.filter(departments__document_departments__id=requested_document_id)

            return queryset

        else:
            raise serializers.ValidationError({"Access Denied": "You are not authorized to view company members."})
                
from rest_framework.views import APIView
        
class BulkUserDeleteAPIView(APIView):
    permission_classes = [IsAdminUserOrReadOnly]
    authentication_classes = [JWTAuthentication]
    def post(self, request, format=None):
        # Extract the list of user IDs from the request data
        user_ids = request.data.get('user_ids', [])

        # Validate that user IDs are provided
        if not user_ids:
            return Response({"message": "User IDs are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.user.role == 'Admin':        
            try:
                admin = AdminUser.objects.get(admin=request.user, is_active=True)
            except AdminUser.DoesNotExist:
                return False

            # Check if the user to be deleted belongs to the same company as the admin
            # Update the is_active field of each user
            for user_id in user_ids:
                try:
                    user = CompaniesTeam.objects.get(id=user_id)
                    if isinstance(user, CompaniesTeam):
                        if user.company == admin.company:
                            user.is_active = False
                            user.save()
                            user_info = CustomUser.objects.filter(email=user.members.email)
                            user_info.delete()
                        else:
                            return Response({"Access Denied": "You are not authorized for this request"}, status=status.HTTP_403_FORBIDDEN)
                except CompaniesTeam.DoesNotExist:
                    return Response({"message": f"User with ID {user_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
        elif request.user.role == 'Super Admin':
            for user_id in user_ids:
                try:
                    user = CompaniesTeam.objects.get(id=user_id)
                    if isinstance(user, CompaniesTeam):
                        # if user.company == admin.company:
                            user.is_active = False
                            user.save()
                        # else:
                        #     return Response({"Access Denied": "You are not authorized for this request"}, status=status.HTTP_403_FORBIDDEN)
                except CompaniesTeam.DoesNotExist:
                    return Response({"message": f"User with ID {user_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message": "Users Deleted successfully"}, status=status.HTTP_200_OK)