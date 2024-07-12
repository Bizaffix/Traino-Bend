from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView , UpdateAPIView
from .serializers import CustomUserDetailSerializer , CustomUserSerializer
from rest_framework.permissions import IsAuthenticated
from accounts.models import CustomUser
from teams.models import CompaniesTeam
from company.models import AdminUser
from rest_framework import status
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from .permissions import IsAdminUserOrReadOnly
from rest_framework import serializers
from company.api.serializers import AdminSerializer 
from teams.api.serializers import CompaniesTeamSerializer
from departments.models import Departments
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings

#nsm
class CustomUserCreateAPIView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def create(self, request, *args, **kwargs):
        if request.user.role == 'Super Admin':
            pass
        elif request.user.role == 'Admin':
            if request.data.get('role') == 'Super Admin':
                return Response({"error": "Admin cannot create Super Admins."}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"error": "You don't have permission to create users."}, status=status.HTTP_403_FORBIDDEN)

        request.data['added_by'] = request.user.id
        new_user_role = request.data.get('role')
        email = request.data.get('email')
        department_ids = request.data.get('departments', [])

        try:
            user_data = CustomUser.objects.filter(email=email).exists()
            if user_data:
                return Response({"error": f"{new_user_role} with this email {email} already exists"}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            pass  # User does not exist, proceed with creation

        password = request.data.pop('password', None)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(password=make_password(password))

        if new_user_role == 'Admin':
            company_id = request.data.get('company')
            if not company_id:
                user.delete()
                raise serializers.ValidationError({"Bad Request": "Company id is required"})

            admin_data = {'email': email, 'company': company_id}
            admin_create = AdminSerializer(data=admin_data)
            if admin_create.is_valid(raise_exception=True):
                admin_create.save()
                self.send_welcome_email(email, password, new_user_role)
            else:
                user.delete()
                return Response(admin_create.errors, status=status.HTTP_400_BAD_REQUEST)

        elif new_user_role == 'User':
            company_id = request.data.get('company')
            if not company_id:
                user.delete()
                raise serializers.ValidationError({"Bad Request": "Company id is required"})

            member_data = {'members': user.id, 'company': company_id}
            member = CompaniesTeamSerializer(data=member_data)
            if member.is_valid(raise_exception=True):
                member_instance = member.save()
            else:
                user.delete()
                return Response(member.errors, status=status.HTTP_400_BAD_REQUEST)

            department_names = []
            valid_department_ids = []
            for department_id in department_ids:
                department = Departments.objects.filter(id=department_id, is_active=True).first()
                if department:
                    department.users.add(member_instance)
                    valid_department_ids.append(department_id)
                    department_names.append(department.name)
                else:
                    user.delete()
                    return Response({"Not Found": f"Department with id {department_id} is not found or is inactive"}, status=status.HTTP_404_NOT_FOUND)

            self.send_welcome_email(email, password, new_user_role)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        response_data = serializer.data
        response_data['department_ids'] = valid_department_ids
        response_data['department_names'] = department_names

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    def send_welcome_email(self, email, password, role):
        if settings.DEBUG:
            login_url = 'https://dashboard.traino.ai/signin/'
        else:
            login_url = 'https://dashboard.traino.ai/signin/'
        
        send_mail(
            subject="Welcome to Traino-ai",
            message=f'''Welcome to Traino-ai.

We're so excited to be working with you, and we want to be sure we start off on the right foot.
Your email and password to access the Traino-ai portal is shown below. Please click here to sign-in.

Username: {email}
Password: {password}
Role: {role}

Please {login_url} and complete your profile.

Regards,
Traino-ai.''',
            from_email="no-reply@traino.ai",
            recipient_list=[email],
            fail_silently=False,
        )
        

#nsm
from .serializers import CustomAdminUpdateSerializer , CustomUserUpdateSerializer
class CustomUserUpdateAPIView(UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check if Admin is trying to update a Super Admin
        if request.user.role == 'Admin' and instance.role == 'Super Admin':
            return Response({"error": "Admin cannot update Super Admins."}, status=status.HTTP_403_FORBIDDEN)

        # Check if the role change is attempted
        if 'role' in request.data and request.data['role'] != instance.role:
            return Response({"error": "Cannot change the role of the user."}, status=status.HTTP_400_BAD_REQUEST)

        # Handle password change
        if 'password' in request.data:
            password = request.data.pop('password')
            instance.set_password(password)
            #instance.save()

        if instance.role == 'Admin':
            serializer = CustomAdminUpdateSerializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        
        if instance.role == 'User':
            serializer = CustomUserUpdateSerializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        
        # Update additional fields based on role
        if (request.user.role == "Super Admin") or (request.user.role == "Admin"):
            if instance.role == 'Admin':
                company_id = request.data.get('company')
                if company_id:
                    admin_instance = AdminUser.objects.get(admin=instance)
                    admin_instance.company_id = company_id
                    admin_instance.save()
            elif instance.role == 'User':
                company_id = request.data.get('company')
                new_department_ids = request.data.get('department_ids', [])

                if company_id:
                    member_instance = CompaniesTeam.objects.get(members__id=instance.id)
                    member_instance.company_id = company_id
                    member_instance.save()

                    if new_department_ids is not None:
                        current_department_ids = list(member_instance.departments_set.values_list('id', flat=True))

                        # Determine departments to add, keep, and remove
                        departments_to_add = set(new_department_ids) - set(current_department_ids)
                        departments_to_keep = set(new_department_ids) & set(current_department_ids)
                        departments_to_remove = set(current_department_ids) - set(new_department_ids)

                        # Handle department assignment
                        for department_id in departments_to_remove:
                            department = Departments.objects.get(id=department_id)
                            department.users.remove(member_instance)
                            department.save()

                        for department_id in departments_to_add:
                            department = Departments.objects.filter(id=department_id, is_active=True).first()
                            if department:
                                department.users.add(member_instance)
                                department.save()
                            else:
                                return Response({"Not Found": f"Department with id {department_id} is not found"}, status=status.HTTP_404_NOT_FOUND)

                        for department_id in departments_to_keep:
                            # No operation needed for kept departments
                            pass

                        # Fetch updated department names
                        updated_departments = Departments.objects.filter(id__in=new_department_ids, is_active=True)
                        department_names = [dept.name for dept in updated_departments]

                        # Return updated data
                        response_data = serializer.data
                        response_data['department_ids'] = new_department_ids
                        response_data['department_names'] = department_names

                        return Response(response_data, status=status.HTTP_200_OK)
                    else:
                        return Response({"not found": "Departments Not Found"}, status=status.HTTP_404_NOT_FOUND)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"Access Denied": "You do not have access to this action"}, status=status.HTTP_401_UNAUTHORIZED)
    
    # def update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     if request.user.role == 'Admin' and instance.role == 'Super Admin':
    #         return Response({"error": "Admin cannot update Super Admins."}, status=status.HTTP_403_FORBIDDEN)

    #     if 'role' in request.data and request.data['role'] != instance.role:
    #         return Response({"error": "Cannot change the role of the user."}, status=status.HTTP_400_BAD_REQUEST)

    #     if 'password' in request.data:
    #         password = request.data.pop('password')
    #         instance.set_password(password)
        
    #     serializer = self.get_serializer(instance, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)

    #     # Update additional fields based on role
    #     if (request.user.role == "Super Admin") or (request.user.role == "Admin"):
    #         if instance.role == 'Admin':
    #             company_id = request.data.get('company')
    #             if company_id:
    #                 admin_instance = AdminUser.objects.get(admin=instance)
    #                 admin_instance.company_id = company_id
    #                 admin_instance.save()
    #         elif instance.role == 'User':
    #             company_id = request.data.get('company')
    #             department_ids = request.data.get('department_ids', [])
    #             if company_id:
    #                 member_instance = CompaniesTeam.objects.get(members__id=instance.id)
    #                 member_instance.company_id = company_id
    #                 member_instance.save()

    #                 if department_ids is not None:
    #                     for department_id in department_ids:
    #                         department = Departments.objects.filter(id=department_id, is_active=True).first()
    #                         if department:
    #                             department.users.add(member_instance)
    #                             department.save()
    #                         else:
    #                             return Response({"Not Found":f"Department with id {department_id} is not found"}, status=status.HTTP_404_NOT_FOUND)
    #                 else:
    #                     raise serializers.ValidationError({"not found":"Departments Not Found"})
    #         return Response(serializer.data, status=status.HTTP_200_OK)

    #     return Response({"Access Denied":"You have access to this action"}, status=status.HTTP_401_UNAUTHORIZED)
            
            
            
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