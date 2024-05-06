from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from .serializers import CustomUserDetailSerializer
from rest_framework.permissions import IsAuthenticated
from accounts.models import CustomUser
from rest_framework import status
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.forms.models import model_to_dict

class LoginAPIView(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')

        # Authenticate user
        user = authenticate(email=email, password=password)

        if user:
            # Generate token
            refresh = RefreshToken.for_user(user)
            token = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            # Additional data checking (e.g., existence in DB)
            try:
                user_data = CustomUser.objects.get(email=email)
                serializer = CustomUserDetailSerializer(user_data)  # Use CustomUserDetailSerializer
                serialized_user = {
                    'id': serializer.data['id'],
                    'email': serializer.data['email'],
                    'role': serializer.data['role'],
                    'created_at': serializer.data['created_at'],
                }
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            return JsonResponse({'token': token, 'user': serialized_user}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# class CustomUserDetailApiView(RetrieveAPIView):
#     serializer_class = CustomUserDetailSerializer
#     permission_classes = [IsAuthenticated]
#     queryset = CustomUser.objects.all()
#     # lookup_field = 'pk'
    
#     def get_object(self):
#         # Return the authenticated user's instance
#         return self.request.user