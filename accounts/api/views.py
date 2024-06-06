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
from company.api.serializers import AdminSerializer 
from company.models import company
from teams.api.serializers import CompaniesTeamSerializer
from departments.models import Departments
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings

class CustomUserCreateAPIView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminUserOrReadOnly]  
    def create(self, request, *args, **kwargs):
        if request.user.role == 'Super Admin':
            pass
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
        department_ids = request.data.get('department_ids', [])
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
        if new_user_role == 'Admin':
            company_id = request.data.get('company')
            if not company_id:
                user.delete()
                raise serializers.ValidationError({"Bad Request":"Company id is required"})
            admin_data = {'email': email, 'company': company_id}
            admin_create = AdminSerializer(data=admin_data)
            if admin_create.is_valid(raise_exception=True):
                admin_create.save()
                if settings.DEBUG:
                    login_url = 'https://dashboard.traino.ai/signin/'
                else:
                    login_url = 'https://dashboard.traino.ai/signin/'
                send_mail(
                subject="Welcome to Traino-ai",
                message=f'''Welcome to Traino-ai.

We're so excited to be working with you, and we want to be sure we start off on the right foot.
Your email and password to access the Traino-ai portal is shown below.Please click here to sign-in.

Username: {email}
Password: {password}
Role: {new_user_role}

Please {login_url} and complete your profile.

Regards
Traino-ai.''',
                from_email="no-reply@traino.ai",
                recipient_list=[email],
                fail_silently=False,
                )
            else:
                user.delete()
                return Response(admin_create.errors, status=status.HTTP_400_BAD_REQUEST)
        elif new_user_role == 'User':
            company_id = request.data.get('company')
            if not company_id:
                user.delete()
                raise serializers.ValidationError({"Bad Request":"Company id is required"})
            member_data = {'members': user.id, 'company': company_id}
            member = CompaniesTeamSerializer(data=member_data)
            if member.is_valid(raise_exception=True):
                member.save()
            else:
                user.delete()
                return Response(admin_create.errors, status=status.HTTP_400_BAD_REQUEST)
            team_member = CompaniesTeam.objects.get(members__email=email)
            for department_id in department_ids:
                department = Departments.objects.filter(id=department_id, is_active=True).first()
                if department:
                    department.users.add(team_member)
                    department.save()
                else:
                    return Response({"Not Found":f"Department with id {department_id} is not found"}, status=status.HTTP_404_NOT_FOUND)
            if settings.DEBUG:
                login_url = 'https://dashboard.traino.ai/signin/'
            else:
                login_url = 'https://dashboard.traino.ai/signin/'
            send_mail(
                subject="Welcome to Traino-ai",
                message=f'''Welcome to Traino-ai.

We're so excited to be working with you, and we want to be sure we start off on the right foot.
Your email and password to access the Traino-ai portal is shown below.Please click here to sign-in.

Username: {email}
Password: {password}
Role: {new_user_role}

Please {login_url} and complete your profile.

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

# class CustomUserUpdateAPIView(UpdateAPIView):
#     queryset = CustomUser.objects.all()
#     serializer_class = CustomUserSerializer
#     permission_classes = [IsAdminUserOrReadOnly, IsActiveAdminPermission]
#     lookup_field = 'id'

#     def put(self, request, *args, **kwargs):
#         instance = self.get_object()
#         if instance.added_by != request.user:
#             return Response({"Account Access Errors": "You don't have permission to update this Account Holder's Details."},
#                             status=status.HTTP_403_FORBIDDEN)

#         return super().update(request, *args, **kwargs)

class CustomUserUpdateAPIView(UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    lookup_field = 'id'
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # if instance.added_by != request.user:
        #     return Response({"Account Access Errors": "You don't have permission to update this Account Holder's Details."},
        #                     status=status.HTTP_403_FORBIDDEN)

        if request.user.role == 'Super Admin' and instance.role != 'Admin':
            return Response({"error": "Super Admin can only update Admins."}, status=status.HTTP_403_FORBIDDEN)
        elif request.user.role == 'Admin' and instance.role != 'User':
            return Response({"error": "Admin can only update Users."}, status=status.HTTP_403_FORBIDDEN)

        if 'role' in request.data and request.data['role'] != instance.role:
            return Response({"error": "Cannot change the role of the user."}, status=status.HTTP_400_BAD_REQUEST)

        if 'password' in request.data:
            password = request.data.pop('password')
            instance.set_password(password)
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Update additional fields based on role
        if instance.role == 'Admin':
            company_id = request.data.get('company')
            if company_id:
                admin_instance = AdminUser.objects.get(email=instance.email)
                admin_instance.company_id = company_id
                admin_instance.save()

            # return Response({"update Successfully":"Admin Updated Successfully"}, status=status.HTTP_200_OK)
            
        elif instance.role == 'User':
            company_id = request.data.get('company')
            department_ids = request.data.get('department_ids', None)
            if company_id:
                member_instance = CompaniesTeam.objects.get(members__id=instance.id)
                member_instance.company_id = company_id
                member_instance.save()


                for department in Departments.objects.filter(users=member_instance):
                    department.users.remove(member_instance)
                # member_instance.departments.clear()
                if department_ids is not None:
                    for department_id in department_ids:
                        department = Departments.objects.filter(id=department_id, is_active=True).first()
                        if department:
                            department.users.add(member_instance)
                        else:
                            return Response({"error": f"Department with id {department_id} not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.data, status=status.HTTP_200_OK)

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
                        return Response({"Unauthorized": "You are blocked or deleted"}, status=status.HTTP_401_UNAUTHORIZED)
                elif serializer.data['role'] == 'User':
                    user_company = CompaniesTeam.objects.get(members=serializer.data['id'])
                    # print(user.company.id)
                    # print(user.company.name)
                    if user_company.is_active==True:
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
                            'member_id':str(user_company.id),
                            'company_name':str(user_company.company.name),
                            'company_id':str(user_company.company.id),
                            'created_at': serializer.data['created_at'],
                        }
                    else:
                        return Response({"Unauthorized": "You are blocked or deleted"}, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    user_data = CustomUser.objects.get(email=email)
                    serializer = CustomUserDetailSerializer(user_data)
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
                        # 'company_id':admin.company.id,
                        # 'company_name':admin.company.name,
                        'created_at': serializer.data['created_at'],
                    }
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            return JsonResponse({'token': token, 'user': serialized_user}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class UserDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            user_data = CustomUser.objects.get(id=user.id)
            serializer = CustomUserDetailSerializer(user_data)
            
            if serializer.data['role'] == 'Admin':
                admin = get_object_or_404(AdminUser, admin=user.id)
                if admin.is_active:
                    # refresh = RefreshToken.for_user(user)
                    # token = {
                    #         'refresh': str(refresh),
                    #         'access': str(refresh.access_token),
                    # }
                    serialized_user = {
                        'id': serializer.data['id'],
                        'first_name': serializer.data['first_name'],
                        'last_name': serializer.data['last_name'],
                        'phone': serializer.data['phone'],
                        'email': serializer.data['email'],
                        'role': serializer.data['role'],
                        'admin_id': str(admin.id),
                        'company_id': str(admin.company.id),
                        'company_name': str(admin.company.name),
                        'created_at': serializer.data['created_at'],
                    }
                else:
                    return Response({"Unauthorized": "You are blocked or deleted"}, status=status.HTTP_401_UNAUTHORIZED)
            elif serializer.data['role'] == 'User':
                user_company = get_object_or_404(CompaniesTeam, members=user.id)
                if user_company.is_active:
                    # refresh = RefreshToken.for_user(user)
                    # token = {
                    #         'refresh': str(refresh),
                    #         'access': str(refresh.access_token),
                    # }
                    serialized_user = {
                        'id': serializer.data['id'],
                        'first_name': serializer.data['first_name'],
                        'last_name': serializer.data['last_name'],
                        'phone': serializer.data['phone'],
                        'email': serializer.data['email'],
                        'role': serializer.data['role'],
                        'member_id': str(user_company.id),
                        'company_name': str(user_company.company.name),
                        'company_id': str(user_company.company.id),
                        'created_at': serializer.data['created_at'],
                    }
                else:
                    return Response({"Unauthorized": "You are blocked or deleted"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                # refresh = RefreshToken.for_user(user)
                # token = {
                #             'refresh': str(refresh),
                #             'access': str(refresh.access_token),
                # }
                serialized_user = {
                    'id': serializer.data['id'],
                    'first_name': serializer.data['first_name'],
                    'last_name': serializer.data['last_name'],
                    'phone': serializer.data['phone'],
                    'email': serializer.data['email'],
                    'role': serializer.data['role'],
                    'created_at': serializer.data['created_at'],
                }
            
            return Response({'user': serialized_user}, status=status.HTTP_200_OK)
        
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)