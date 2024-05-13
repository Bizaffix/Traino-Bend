from teams.models import CompaniesTeam
from rest_framework.generics import (
    CreateAPIView, UpdateAPIView , RetrieveAPIView , DestroyAPIView, ListAPIView
)
from .serializers import CompaniesTeamSerializer , CompaniesTeamDetailsSerializers
from .permissions import IsAdminUserOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from .permissions import IsAdminUserOrReadOnly, IsActiveAdminPermission
from rest_framework import serializers
from company.models import AdminUser

class AddMembersApiView(CreateAPIView):
    serializer_class = CompaniesTeamSerializer
    permission_classes = [IsAdminUserOrReadOnly, IsActiveAdminPermission]

class MembersUpdateDestroyApiView(RetrieveAPIView , UpdateAPIView, DestroyAPIView):
    serializer_class = CompaniesTeamDetailsSerializers
    permission_classes = [IsAdminUserOrReadOnly, IsActiveAdminPermission]
    queryset = CompaniesTeam.objects.filter(is_active=True)
    
    def put(self , request , *args, **kwargs):
        CompaniesTeam.objects.get(id=self.kwargs['id'])
        return self.update(request, *args , **kwargs)
    
    def delete(self , request , *args , **kwargs):
        instance = self.get_object()
        instance.is_active=False
        instance.save()
        return Response({"Delete Status": "Successfully Removed the User" , "Deleted user_id":instance.id}, status=status.HTTP_202_ACCEPTED)

    
class MembersListApiView(ListAPIView):
    serializer_class = CompaniesTeamDetailsSerializers
    permission_classes = [IsAdminUserOrReadOnly, IsActiveAdminPermission]
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
        else:
            raise serializers.ValidationError({"Access Denied":"You are not authorized to view company members."})