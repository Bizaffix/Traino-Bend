from rest_framework.generics import RetrieveAPIView
from .serializers import CustomUserDetailSerializer
from rest_framework.permissions import IsAuthenticated
from accounts.models import CustomUser

class CustomUserDetailApiView(RetrieveAPIView):
    serializer_class = CustomUserDetailSerializer
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()
    # lookup_field = 'pk'
    
    def get_object(self):
        # Return the authenticated user's instance
        return self.request.user