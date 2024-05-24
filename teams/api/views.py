from teams.models import CompaniesTeam
from rest_framework.generics import (
    CreateAPIView, UpdateAPIView , RetrieveAPIView , DestroyAPIView, ListAPIView
)
from .serializers import CompaniesTeamSerializer , CompaniesTeamDetailsSerializers
from .permissions import IsAdminUserOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication 
from .permissions import IsAdminUserOrReadOnly, IsActiveAdminPermission , IsActiveAdminUsersPermission
from rest_framework import serializers
from company.models import AdminUser

class AddMembersApiView(CreateAPIView):
    serializer_class = CompaniesTeamSerializer
    permission_classes = [IsAdminUserOrReadOnly, IsActiveAdminPermission]
    authentication_classes = [JWTAuthentication]
    
    def perform_create(self , serializer):
        serializer.save(is_active=True)

class MembersUpdateDestroyApiView(RetrieveAPIView , UpdateAPIView, DestroyAPIView):
    serializer_class = CompaniesTeamDetailsSerializers
    permission_classes = [IsAdminUserOrReadOnly]
    authentication_classes = [JWTAuthentication]
    queryset = CompaniesTeam.objects.filter(is_active=True)
    lookup_field = 'id'
    
    def put(self , request , *args, **kwargs):
        CompaniesTeam.objects.get(id=self.kwargs['id'])
        return self.update(request, *args , **kwargs)
    
    def delete(self , request , *args , **kwargs):
        instance = self.get_object()
        instance.is_active=False
        instance.save()
        return Response({"Delete Status": "Successfully Removed the User" , "id":instance.id}, status=status.HTTP_202_ACCEPTED)


from rest_framework.filters import SearchFilter, OrderingFilter
    
class MembersListApiView(ListAPIView):
    serializer_class = CompaniesTeamDetailsSerializers
    permission_classes = [IsAdminUserOrReadOnly, IsActiveAdminPermission]#, IsActiveAdminUsersPermission
    authentication_classes = [JWTAuthentication]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','members__first_name', 'members__last_name', 'members__email', 'members__phone', 'members__role']
    ordering_fields = ['id','members__first_name', 'members__last_name', 'members__email', 'members__phone', 'members__role']
    ordering = ['id','members__first_name', 'members__last_name', 'members__email', 'members__phone', 'members__role']  # Default ordering (A-Z by company_name)
    queryset = CompaniesTeam.objects.filter(is_active=True)
    
    def get_queryset(self):
        user = self.request.user

        # Check if the user is an admin
        if user.role == "Admin":
            try:
                admin_user = AdminUser.objects.get(admin=user, is_active=True)
                company = admin_user.company
            except AdminUser.DoesNotExist:
                raise serializers.ValidationError({"Admin Error":"Admin Account is Deleted By Super Admin. You can no longer request that"})

            queryset = CompaniesTeam.objects.filter(company=company, is_active=True)

            # Check if the request is filtered by company
            requested_company_id = self.request.query_params.get('company_id')
            if requested_company_id:
                if str(requested_company_id) != str(company.id):
                    raise serializers.ValidationError({"Access Denied":"You are not allowed to view users of another company."})
                else:
                    queryset = queryset.filter(company=requested_company_id)
            return queryset
        elif user.role == "Super Admin":
            requested_company_id = self.request.query_params.get('company_id')
            if requested_company_id is not None:
                queryset = self.queryset.filter(company=requested_company_id)
                return queryset
            else:
                return self.queryset
        else:
            raise serializers.ValidationError({"Access Denied":"You are not authorized to view company members."})
        
        
from rest_framework.views import APIView
        
class BulkUserDeleteAPIView(APIView):
    permission_classes = [IsAdminUserOrReadOnly, IsActiveAdminUsersPermission]
    authentication_classes = [JWTAuthentication]
    def post(self, request, format=None):
        # Extract the list of user IDs from the request data
        user_ids = request.data.get('user_ids', [])

        # Validate that user IDs are provided
        if not user_ids:
            return Response({"message": "User IDs are required"}, status=status.HTTP_400_BAD_REQUEST)

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
                    else:
                        return Response({"Access Denied": "You are not authorized for this request"}, status=status.HTTP_403_FORBIDDEN)
            except CompaniesTeam.DoesNotExist:
                return Response({"message": f"User with ID {user_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Users Deleted successfully"}, status=status.HTTP_200_OK)