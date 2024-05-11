from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView , CreateAPIView , UpdateAPIView, DestroyAPIView
from .serializers import CustomUserDetailSerializer , CustomUserSerializer
from rest_framework.permissions import IsAuthenticated
from accounts.models import CustomUser
from rest_framework import status
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import make_password


class CustomUserCreateAPIView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]  
    def create(self, request, *args, **kwargs):
        if request.user.role == 'Super Admin':
            if request.data.get('role') != 'Admin':
                return Response({"error": "Super Admin can only create Admins."},
                                status=status.HTTP_403_FORBIDDEN)
        elif request.user.role == 'Admin':
            if request.data.get('role') != 'User':
                return Response({"error": "Admin can only create Users."},
                                status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"error": "You don't have permission to create users."},
                            status=status.HTTP_403_FORBIDDEN)
            
        request.data['added_by'] = request.user.id
        password = request.data.pop('password', None) 
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(password=make_password(password))
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CustomUserUpdateAPIView(UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        # instance = CustomUser.objects.filter(id=self.kwargs['id'])

        # Check if the authenticated user is the creator of the instance
        if instance.added_by != request.user:
            return Response({"error": "You don't have permission to update this Account Holder's Details."},
                            status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)

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