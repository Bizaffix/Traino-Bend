from teams.models import CompaniesTeam
from rest_framework.generics import (
    CreateAPIView, UpdateAPIView , RetrieveAPIView , DestroyAPIView, ListAPIView
)
from .serializers import CompaniesTeamSerializer , CompaniesTeamDetailsSerializers
from .permissions import IsAdminUserOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from .permissions import IsAdminUserOrReadOnly

class AddMembersApiView(CreateAPIView):
    serializer_class = CompaniesTeamSerializer
    permission_classes = [IsAdminUserOrReadOnly]

class MembersUpdateDestroyApiView(RetrieveAPIView , UpdateAPIView, DestroyAPIView):
    serializer_class = CompaniesTeamDetailsSerializers
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = CompaniesTeam.objects.filter(is_active=True)
    
    def put(self , request , *args, **kwargs):
        CompaniesTeam.objects.get(id=self.kwargs['id'])
        return self.update(request, *args , **kwargs)
    
    def delete(self , request , *args , **kwargs):
        instance = self.get_object()
        instance.is_active=False
        instance.save()
        return Response({"Delete Status": "Successfully Removed the User" , "Deleted User's Id":instance.id}, status=status.HTTP_202_ACCEPTED)

    
class MembersListApiView(ListAPIView):
    serializer_class = CompaniesTeamDetailsSerializers
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = CompaniesTeam.objects.filter(is_active=True)
    
    def get_queryset(self):
        queryset = CompaniesTeam.objects.filter(is_active=True)
        searched_data = self.request.query_params.get("q", None)
        if searched_data:
            searched_queryset = queryset.filter(company_name__icontains=searched_data)
            return searched_queryset
        else:
            return queryset