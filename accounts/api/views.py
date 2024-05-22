from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView , CreateAPIView , UpdateAPIView, DestroyAPIView
from .serializers import CustomUserDetailSerializer , CustomUserSerializer
from rest_framework.permissions import IsAuthenticated
from accounts.models import CustomUser
from teams.models import CompaniesTeam
from company.models import company , AdminUser
from rest_framework import status
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import make_password
from .permissions import IsAdminUserOrReadOnly
from rest_framework import serializers
from django.core.mail import send_mail


class CustomUserCreateAPIView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminUserOrReadOnly]  
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
        new_user_role = request.data.get('role')
        email = request.data.get('email')
        try:
            user_data = CustomUser.objects.get(email=email)
            if user_data:
                raise serializers.ValidationError(
                    {"Account Exists": f"{new_user_role} with this email {email} already exists"})
        except CustomUser.DoesNotExist:
            # User does not exist, so continue with user creation
            pass
        password = request.data.pop('password', None) 
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(password=make_password(password))
        send_mail(
            subject="Welcome to Traino-ai",
            message=f'''Welcome to Traino-ai.

We're so excited to be working with you, and we want to be sure we start off on the right foot.
Your email and password to access the Traino-ai portal is shown below.Please click here to sign-in.

Username: {email}
Password: {password}
Role: {new_user_role}

Please log in and complete your profile.

Regards
Traino-ai.''',
            from_email="no-reply@traino.ai",
            recipient_list=[email],
            fail_silently=False,
        )
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
from teams.api.permissions import IsActiveAdminPermission

class CustomUserUpdateAPIView(UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminUserOrReadOnly, IsActiveAdminPermission]
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.added_by != request.user:
            return Response({"Account Access Errors": "You don't have permission to update this Account Holder's Details."},
                            status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)

class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')

        # Authenticate user
        user = authenticate(email=email, password=password)

        if user:
            # Additional data checking (e.g., existence in DB)
            try:
                user_data = CustomUser.objects.get(email=email)
                serializer = CustomUserDetailSerializer(user_data)  # Use CustomUserDetailSerializer
                if serializer.data['role'] == 'Admin':
                    admin = AdminUser.objects.get(admin=serializer.data['id'])
                    # print(admin.company.id)
                    # print(admin.company.name)
                    # print(admin.is_active == True)
                    if admin.is_active==True:
                        refresh = RefreshToken.for_user(user)
                        token = {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        }
                        serialized_user = {
                            'id': serializer.data['id'],
                            'first_name': serializer.data['first_name'],
                            'last_name': serializer.data['last_name'],
                            'phone': serializer.data['phone'],
                            'email': serializer.data['email'],
                            'role': serializer.data['role'],
                            'admin_id':str(admin.id),
                            'company_id':str(admin.company.id),
                            'company_name':str(admin.company.name),
                            'created_at': serializer.data['created_at'],
                        }
                    else:
                        return Response({"Not Found":"No Account Found against these credentials"})
                elif serializer.data['role'] == 'User':
                    user = CompaniesTeam.objects.get(members=serializer.data['id'])
                    # print(user.company.id)
                    # print(user.company.name)
                    if user.is_active==True:
                        refresh = RefreshToken.for_user(user)
                        token = {
                            'refresh': str(refresh),
                            'access': str(refresh.access_token),
                        }
                        serialized_user = {
                            'id': serializer.data['id'],
                            'first_name': serializer.data['first_name'],
                            'last_name': serializer.data['last_name'],
                            'phone': serializer.data['phone'],
                            'email': serializer.data['email'],
                            'role': serializer.data['role'],
                            'company_id':str(user.company.id),
                            'company_name':str(user.company.name),
                            'created_at': serializer.data['created_at'],
                        }
                    else:
                        return Response({"Not Found":"No Account Found Against These Credentials"})
                else:
                    user_data = CustomUser.objects.get(email=email)
                    serializer = CustomUserDetailSerializer(user_data)  # Use CustomUserDetailSerializer
                    serialized_user = {
                        'id': serializer.data['id'],
                        'first_name': serializer.data['first_name'],
                        'last_name': serializer.data['last_name'],
                        'phone': serializer.data['phone'],
                        'email': serializer.data['email'],
                        'role': serializer.data['role'],
                        # 'company_id':admin.company.id,
                        # 'company_name':admin.company.name,
                        'created_at': serializer.data['created_at'],
                    }
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            return JsonResponse({'token': token, 'user': serialized_user}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
