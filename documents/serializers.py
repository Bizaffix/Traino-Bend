from rest_framework import serializers
from departments.models import DepartmentsDocuments , Departments
from django.utils import timezone
from teams.models import CompaniesTeam
from django.core.mail import send_mail
from django.conf import settings
from documents.models import DocumentQuiz, QuizQuestions, ScheduleDetail

class DepartmentsDocumentsSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField(read_only=True)
    last_name = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)
    phone = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)
    assigned_users = serializers.SerializerMethodField(read_only=True)
    is_summary = serializers.BooleanField(read_only=True)
    is_keypoints = serializers.BooleanField(read_only=True)
    is_quizzes = serializers.BooleanField(read_only=True)
    quizzes = serializers.SerializerMethodField(read_only=True)
    assigned_users_details = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = DepartmentsDocuments
        fields = '__all__'

    def get_first_name(self , obj):
        return obj.added_by.first_name
    
    def get_last_name(self , obj):
        return obj.added_by.last_name
    
    def get_email(self , obj):
        return obj.added_by.email
    
    def get_phone(self , obj):
        return str(obj.added_by.phone)
        
    def get_created_at(self, obj):
        return obj.created_at
    
    def get_quizzes(self, obj):
        return obj.quizzes
    
    def get_assigned_users(self, obj):
        return [user.id for user in obj.assigned_users.all()]
    
    def get_assigned_users_details(self, obj):
        return [{"id": user.id, "first_name": user.members.first_name, "last_name":user.members.last_name, "email":user.members.email} for user in obj.assigned_users.all()]

# class UserDetailSerializer(serializers.Serializer):
#     id = serializers.UUIDField(format='hex_verbose')
#     quiz_id = serializers.UUIDField(format='hex_verbose')
#     question_id = serializers.UUIDField(format='hex_verbose')

class UserDetailSerializer(serializers.Serializer):
    id = serializers.CharField()
    quiz_id = serializers.CharField()
    question_id = serializers.CharField()

class DepartmentsDocumentsUpdateSerializer(serializers.ModelSerializer):
    department_ids = serializers.ListField(
        child=serializers.UUIDField(format='hex_verbose'), required=True, write_only=True,
    )
    users = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        ), 
        required=False, 
        write_only=True,
    )
    # users = serializers.ListField(
    #     child=serializers.UUIDField(format='hex_verbose'),
    #     required=False,
    #     write_only=True,
    #     # error_messages={'required': 'This field is required.'}
    # )
    # users = serializers.ListField(
    #     child=UserDetailSerializer(), required=False, write_only=True,
    # )
    first_name = serializers.SerializerMethodField(read_only=True)
    last_name = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)
    phone = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)
    assigned_users_details = serializers.SerializerMethodField(read_only=True)
    all = serializers.BooleanField(required=False, write_only=True)
    is_summary = serializers.BooleanField(read_only=True)
    is_keypoints = serializers.BooleanField(read_only=True)
    is_quizzes = serializers.BooleanField(read_only=True)
    schedule_frequency = serializers.CharField(required=False)
    quiz_id = serializers.UUIDField(required=False, allow_null=True)  # New field
    question_id = serializers.UUIDField(required=False, allow_null=True)  # New field


    class Meta:
        model = DepartmentsDocuments
        fields = '__all__'

    def get_first_name(self, obj):
        return obj.added_by.first_name
    
    def get_last_name(self, obj):
        return obj.added_by.last_name
    
    def get_email(self, obj):
        return obj.added_by.email
    
    def get_phone(self, obj):
        return str(obj.added_by.phone)
        
    def get_created_at(self, obj):
        return obj.created_at

    def get_assigned_users_details(self, obj):
        return [{"id": user.id, "first_name": user.members.first_name, "last_name":user.members.last_name,"email":user.members.email} for user in obj.assigned_users.all()]

    def update(self, instance, validated_data):
        users = validated_data.pop('users', [])
        instance.users = users
        # instance.question_id = question_id
        #get data from body
        new_department_ids = validated_data.pop('department_ids', [])
        all_flag = validated_data.pop('all', False)
        new_user_ids = CompaniesTeam.objects.filter(departments__id__in=new_department_ids) if all_flag else validated_data.pop('users', [])
        name = validated_data.pop('name', "")

        # Get current department and user associations
        current_department_id = instance.department.id if instance.department else None
        current_user_ids = list(instance.assigned_users.values_list('id', flat=True))

        # Determine departments to add, keep, and remove
        departments_to_add = set(new_department_ids) - ({current_department_id} if current_department_id else set())
        departments_to_keep = {current_department_id} & set(new_department_ids) if current_department_id else set()
        departments_to_remove = {current_department_id} - set(new_department_ids) if current_department_id else set()

        # Determine users to add, keep, and remove
        users_to_add = set(new_user_ids) - set(current_user_ids)
        users_to_keep = set(new_user_ids) & set(current_user_ids)
        users_to_remove = set(current_user_ids) - set(new_user_ids)

        # Handle department assignment
        for department_id in departments_to_remove:
            instance.department = None
            instance.save()

        for department_id in departments_to_add:
            instance.department = Departments.objects.get(id=department_id)
            instance.save()
        # Handle user assignment
        if all_flag:
            assigned_users = CompaniesTeam.objects.filter(departments__id__in=new_department_ids)
            firstQuiz= DocumentQuiz.objects.filter(document=instance.id).order_by('created_at').first()
            first_question = QuizQuestions.objects.filter(quiz_id=firstQuiz).order_by('created_at').first()

            instance.assigned_users.set(assigned_users)

            instance.assigned_users.set(assigned_users)
            
            subject = 'Assigning Document'
            from_email = 'no-reply@traino.ai'
            message = f'The document {name} has been assigned to you by the admin'
            for user_id in users_to_add:
                recipient_list=[str(user_id).split(" with role User")[0]]
                try:
                    send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list, fail_silently=False)
                    print("Successfully Sent")
                except Exception as e:
                    print(f'Something went wrong: {e}')

        else:
            for user_id in users_to_remove:
                user_instance = CompaniesTeam.objects.get(id=user_id)
       
                instance.assigned_users.remove(user_instance)
                for deleteUser in deleteUsers:
                    deleteUser.delete()
                    instance.assigned_users_data.remove(deleteUser)


                subject = 'Un-Assigning Document'
                from_email = 'no-reply@traino.ai'
                recipient_list=[str(CompaniesTeam.objects.get(id=user_id)).split(" with role User")[0]]
                message = f'The document {name} has been un-assigned to you by the admin'
                try:
                    send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list, fail_silently=False)
                    print("Successfully Sent")
                except Exception as e:
                    print(f'Something went wrong: {e}')


            for user_id in users_to_add:
                try:
                    if CompaniesTeam.objects.filter(id=user_id, departments__id__in=new_department_ids).exists():
                        user_instance = CompaniesTeam.objects.get(id=user_id)
                        instance.assigned_users.add(user_instance)

                        # firstQuiz = DocumentQuiz.objects.filter(document=instance.id).order_by('created_at').first()
                        # first_question = QuizQuestions.objects.filter(quiz_id=firstQuiz).order_by('created_at').first()

                    subject = 'Assigning Document'
                    from_email = 'no-reply@traino.ai'
                    recipient_list = [user_instance.email]  # Assuming `email` field exists
                    message = f'The document {name} has been assigned to you by the admin'
                    try:
                        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list, fail_silently=False)
                        print("Successfully Sent")
                    except Exception as e:
                        print(f'Something went wrong: {e}')
                except CompaniesTeam.DoesNotExist:
                     print(f'User with id {user_id} does not exist.')
            
       
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        schedule_details_list = []
        for user_data in users:
            # Update existing ScheduleDetail if document_id and user_id match, or create a new one
            schedule_detail, created = ScheduleDetail.objects.update_or_create(
                user_id=user_data['id'],
                department_id=instance.department.id if instance.department else None,
                defaults={
                    "quiz_id": user_data['quiz_id'],
                    "question_id": user_data['question_id'],
                    "department_id": instance.department.id if instance.department else None,
                }
            )
            
            # Add the schedule detail to the list
            schedule_details_list.append({
                "quiz_id": schedule_detail.quiz_id,
                "question_id": schedule_detail.question_id,
                "user_id": schedule_detail.user_id,
                "department_id": schedule_detail.department_id,
            })

        instance.save()
        return instance



        
class DepartmentsDocumentsCreateSerializer(serializers.ModelSerializer):
    department_ids = serializers.ListField(
        child=serializers.UUIDField(format='hex_verbose'), write_only=True
    )
    user_ids = serializers.ListField(
        child=serializers.UUIDField(format='hex_verbose'), write_only=True , required=False
    )
    all = serializers.BooleanField(write_only=True, required=False, default=False)
    schedule_time = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = DepartmentsDocuments
        fields = ['id', 'name', 'file', 'department_ids', 'all', 'user_ids', 'schedule_time', 'published', 'added_by', 'created_at']

    def validate_department_ids(self, value):
        # Check if all departments are active
        for department_id in value:
            if not Departments.objects.filter(id=department_id, is_active=True).exists():
                raise serializers.ValidationError({"department not found": f"Department with ID {department_id} is not active or does not exist."})
        return value

    def validate_team_ids(self, value):
        # Check if all teams are active
        for team_id in value:
            if not CompaniesTeam.objects.filter(id=team_id, is_active=True).exists():
                raise serializers.ValidationError({"team not found": f"Team with ID {team_id} is not active or does not exist."})
        return value

    def create(self, validated_data):
        department_ids = validated_data.pop('department_ids')
        user_ids = validated_data.pop('user_ids', [])
        all_users = validated_data.pop('all', False)
        schedule_time = validated_data.pop('schedule_time', timezone.now())
        added_by = validated_data.pop('added_by')
        file = validated_data.pop('file')
        name = validated_data.pop('name')
        published = validated_data.pop('published', False)

        documents = []
        for department_id in department_ids:
            department = Departments.objects.get(id=department_id, is_active=True)
            document = DepartmentsDocuments.objects.create(
                name=name,
                added_by=added_by,
                file=file,
                department=department,
                scheduled_time=schedule_time if schedule_time > timezone.now() else timezone.now(),
                published=published
            )

            if all_users:
                assigned_users = CompaniesTeam.objects.filter(departments__id=department_id)
            else:
                valid_team_ids = [user_id for user_id in user_ids if CompaniesTeam.objects.filter(id=user_id, department=department, is_active=True).exists()]
                assigned_users = CompaniesTeam.objects.filter(id__in=valid_team_ids)

            document.assigned_users.set(assigned_users)
            documents.append(document)

        return documents