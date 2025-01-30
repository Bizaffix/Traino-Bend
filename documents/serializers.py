from rest_framework import serializers
from departments.models import DepartmentsDocuments, Departments
from django.utils import timezone
from teams.models import CompaniesTeam
from django.core.mail import send_mail
from django.conf import settings
from documents.models import DocumentQuiz, QuizQuestions, ScheduleDetail

# class DepartmentsDocumentsSerializer(serializers.ModelSerializer):
#     first_name = serializers.SerializerMethodField(read_only=True)
#     last_name = serializers.SerializerMethodField(read_only=True)
#     email = serializers.SerializerMethodField(read_only=True)
#     phone = serializers.SerializerMethodField(read_only=True)
#     created_at = serializers.SerializerMethodField(read_only=True)
#     assigned_users = serializers.SerializerMethodField(read_only=True)
#     is_summary = serializers.BooleanField(read_only=True)
#     is_keypoints = serializers.BooleanField(read_only=True)
#     is_quizzes = serializers.BooleanField(read_only=True)
#     quizzes = serializers.SerializerMethodField(read_only=True)
#     assigned_users_details = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = DepartmentsDocuments
#         fields = '__all__'

#     def get_first_name(self , obj):
#         return obj.added_by.first_name

#     def get_last_name(self , obj):
#         return obj.added_by.last_name

#     def get_email(self , obj):
#         return obj.added_by.email

#     def get_phone(self , obj):
#         return str(obj.added_by.phone)

#     def get_created_at(self, obj):
#         return obj.created_at

#     def get_quizzes(self, obj):
#         return obj.quizzes

#     def get_assigned_users(self, obj):
#         return [user.id for user in obj.assigned_users.all()]

#     def get_assigned_users_details(self, obj):
#         assigned_users_details=[]
#         for user in obj.assigned_users.all():
#             schedule_details=ScheduleDetail.objects.get(user_id=user.id,document_id=obj.id)
#             assigned_user_details={"id": user.id,
#                                     "first_name": user.members.first_name,
#                                     "last_name":user.members.last_name,
#                                     "email":user.members.email,
#                                     "quiz_id":  schedule_details.quiz_id if schedule_details is not None else None ,
#                                     "question_id": schedule_details.question_id if schedule_details is not None else None
#                                     }
#             assigned_users_details.append(assigned_user_details)

#         return assigned_users_details


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
    dueDate = serializers.DateField(read_only=True)
    avgCompletionTime = serializers.IntegerField(read_only=True)
    overview = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)

    class Meta:
        model = DepartmentsDocuments
        fields = "__all__"

    def get_dueDate(self, obj):
        return obj.added_by.dueDate

    def get_avgCompletionTime(self, obj):
        return obj.added_by.avgCompletionTime

    def get_overview(self, obj):
        return obj.added_by.overview

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

    def get_quizzes(self, obj):
        # pass
        return obj.quizzes

    def get_assigned_users(self, obj):
        return [user.id for user in obj.assigned_users.all()]

    def get_assigned_users_details(self, obj):
        assigned_users_details = []
        for user in obj.assigned_users.all():
            try:
                schedule_details = ScheduleDetail.objects.get(
                    user_id=user.id, document_id=obj.id
                )
                assigned_user_details = {
                    "id": user.id,
                    "first_name": user.members.first_name,
                    "last_name": user.members.last_name,
                    "email": user.members.email,
                    "quiz_id": schedule_details.quiz_id if schedule_details else None,
                    "question_id": (
                        schedule_details.question_id if schedule_details else None
                    ),
                }
            except ScheduleDetail.DoesNotExist:
                assigned_user_details = {
                    "id": user.id,
                    "first_name": user.members.first_name,
                    "last_name": user.members.last_name,
                    "email": user.members.email,
                    "quiz_id": None,
                    "question_id": None,
                }

            assigned_users_details.append(assigned_user_details)

        return assigned_users_details


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
        child=serializers.UUIDField(format="hex_verbose"),
        required=True,
        write_only=True,
    )
    user_ids = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        write_only=True,
    )
    users = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        write_only=True,
    )
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
        fields = "__all__"

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
        return [
            {
                "id": user.id,
                "first_name": user.members.first_name,
                "last_name": user.members.last_name,
                "email": user.members.email,
            }
            for user in obj.assigned_users.all()
        ]

    def update(self, instance, validated_data):
        users = validated_data.pop("user_ids", [])
        instance.users = users
        # get data from body
        new_department_ids = validated_data.pop("department_ids", [])
        all_flag = validated_data.pop("all", False)
        # Step 1: Extract the user IDs from the users list
        extracted_user_ids = [user for user in users]

        # Step 2: Perform the query based on the all_flag
        if all_flag:
            # Query CompaniesTeam based on the extracted user IDs and department IDs
            new_user_ids = CompaniesTeam.objects.filter(
                departments__id__in=new_department_ids
            ).values_list("id", flat=True)
        else:
            # Use the extracted user IDs directly
            new_user_ids = extracted_user_ids

        # Step 3: Print the results for debugging
        name = validated_data.pop("name", "")

        # Get current department and user associations
        current_department_id = list(instance.departments.values_list("id", flat=True))
        current_user_ids = list(instance.assigned_users.values_list("id", flat=True))

        # Determine departments to add, keep, and remove
        departments_to_add = set(new_department_ids) - set(current_department_id)
        departments_to_remove = set(current_department_id) - set(new_department_ids)

        # Determine users to add, keep, and remove
        users_to_add = set(new_user_ids) - set(current_user_ids)
        users_to_remove = set(current_user_ids) - set(new_user_ids)

        # Handle department assignment
        for department_id in departments_to_remove:
            department_to_remove = Departments.objects.get(id=department_id)
            instance.departments.remove(department_to_remove)
            instance.save()

        for department_id in departments_to_add:
            department_to_add = Departments.objects.get(id=department_id)
            instance.departments.add(department_to_add)
            instance.save()
        # Handle user assignment

        firstQuiz = (
            DocumentQuiz.objects.filter(document=instance.id)
            .order_by("created_at")
            .first()
            .id
        )
        first_question = (
            QuizQuestions.objects.filter(quiz_id=firstQuiz)
            .order_by("created_at")
            .first()
            .id
        )
        if all_flag:
            assigned_users = CompaniesTeam.objects.filter(
                departments__id__in=new_department_ids
            )

            instance.assigned_users.set(assigned_users)
            schedule_details_list = []
            for user_data in assigned_users:
                if user_data.id in current_user_ids:
                    print("user already present")
                else:
                    schedule_detail, created = ScheduleDetail.objects.update_or_create(
                        user_id=user_data.id,
                        document_id=instance.id,
                        defaults={
                            "quiz_id": firstQuiz,
                            "question_id": first_question,
                            "document_id": instance.id,
                        },
                    )

                    # Add the schedule detail to the list
                    schedule_details_list.append(
                        {
                            "quiz_id": schedule_detail.quiz_id,
                            "question_id": schedule_detail.question_id,
                            "user_id": schedule_detail.user_id,
                            "document_id": schedule_detail.document_id,
                        }
                    )
                    print("new user id added.")
                # Update existing ScheduleDetail if document_id and user_id match, or create a new one

            instance.save()

            subject = "Assigning Document"
            from_email = "no-reply@traino.ai"
            message = f"The document {name} has been assigned to you by the admin"
            for user_id in users_to_add:
                recipient_list = [str(user_id).split(" with role User")[0]]
                # try:
                #     send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list, fail_silently=False)
                #     print("Successfully Sent")
                # except Exception as e:
                #     print(f'Something went wrong: {e}')

        else:
            for user_id in users_to_remove:
                user_instance = CompaniesTeam.objects.get(id=user_id)
                instance.assigned_users.remove(user_instance)
                instance.save()

                deleteUsers = ScheduleDetail.objects.filter(
                    user_id=user_id, document_id=instance.id
                )
                for deleteUser in deleteUsers:
                    deleteUser.delete()

                subject = "Un-Assigning Document"
                from_email = "no-reply@traino.ai"
                recipient_list = [
                    str(CompaniesTeam.objects.get(id=user_id)).split(" with role User")[
                        0
                    ]
                ]
                message = (
                    f"The document {name} has been un-assigned to you by the admin"
                )
                # try:
                #     send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list, fail_silently=False)
                #     print("Successfully Sent")
                # except Exception as e:
                #     print(f'Something went wrong: {e}')

            for user_id in users_to_add:
                print("users_to_add:", user_id)
                try:
                    user_instance = CompaniesTeam.objects.filter(id=user_id).first()
                    if CompaniesTeam.objects.filter(
                        id=user_id, departments__id__in=new_department_ids
                    ).exists():
                        user_instance = CompaniesTeam.objects.filter(id=user_id).first()
                        instance.assigned_users.add(user_instance)

                        schedule_details_list = []

                        # Update existing ScheduleDetail if document_id and user_id match, or create a new one
                        schedule_detail, created = (
                            ScheduleDetail.objects.update_or_create(
                                user_id=user_id,
                                document_id=instance.id,
                                defaults={
                                    "quiz_id": firstQuiz,
                                    "question_id": first_question,
                                    "document_id": instance.id,
                                },
                            )
                        )

                        # Add the schedule detail to the list
                        schedule_details_list.append(
                            {
                                "quiz_id": schedule_detail.quiz_id,
                                "question_id": schedule_detail.question_id,
                                "user_id": schedule_detail.user_id,
                                "document_id": schedule_detail.document_id,
                            }
                        )

                        # firstQuiz = DocumentQuiz.objects.filter(document=instance.id).order_by('created_at').first()
                        # first_question = QuizQuestions.objects.filter(quiz_id=firstQuiz).order_by('created_at').first()
                    subject = "Assigning Document"
                    from_email = "no-reply@traino.ai"
                    recipient_list = [
                        str(CompaniesTeam.objects.get(id=user_id)).split(
                            " with role User"
                        )[0]
                    ]
                    message = (
                        f"The document {name} has been assigned to you by the admin"
                    )
                    # try:
                    #     send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list, fail_silently=False)
                    #     print("Successfully Sent")
                    # except Exception as e:
                    #     print(f'Something went wrong: {e}')
                except CompaniesTeam.DoesNotExist:
                    print(f"User with id {user_id} does not exist.")

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class DepartmentsDocumentsCreateSerializer(serializers.ModelSerializer):
    department_ids = serializers.ListField(
        child=serializers.UUIDField(format="hex_verbose"), write_only=True
    )
    user_ids = serializers.ListField(
        child=serializers.UUIDField(format="hex_verbose"),
        write_only=True,
        required=False,
    )
    all = serializers.BooleanField(write_only=True, required=False, default=False)
    schedule_time = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = DepartmentsDocuments
        fields = [
            "id",
            "name",
            "file",
            "department_ids",
            "all",
            "user_ids",
            "schedule_time",
            "published",
            "added_by",
            "created_at",
            "dueDate",
            "avgCompletionTime",
            "overview",
        ]

    def validate_department_ids(self, value):
        # Check if all departments are active
        for department_id in value:
            if not Departments.objects.filter(
                id=department_id, is_active=True
            ).exists():
                raise serializers.ValidationError(
                    {
                        "department not found": f"Department with ID {department_id} is not active or does not exist."
                    }
                )
        return value

    def validate_team_ids(self, value):
        # Check if all teams are active
        for team_id in value:
            if not CompaniesTeam.objects.filter(id=team_id, is_active=True).exists():
                raise serializers.ValidationError(
                    {
                        "team not found": f"Team with ID {team_id} is not active or does not exist."
                    }
                )
        return value

    def create(self, validated_data):
        department_ids = validated_data.pop("department_ids")
        user_ids = validated_data.pop("user_ids", [])
        all_users = validated_data.pop("all", False)
        schedule_time = validated_data.pop("schedule_time", timezone.now())
        added_by = validated_data.pop("added_by")
        file = validated_data.pop("file")
        name = validated_data.pop("name")
        published = validated_data.pop("published", False)

        documents = []
        for department_id in department_ids:
            department = Departments.objects.get(id=department_id, is_active=True)
            document = DepartmentsDocuments.objects.create(
                name=name,
                added_by=added_by,
                file=file,
                department=department,
                scheduled_time=(
                    schedule_time if schedule_time > timezone.now() else timezone.now()
                ),
                published=published,
            )

            if all_users:
                assigned_users = CompaniesTeam.objects.filter(
                    departments__id=department_id
                )
            else:
                valid_team_ids = [
                    user_id
                    for user_id in user_ids
                    if CompaniesTeam.objects.filter(
                        id=user_id, department=department, is_active=True
                    ).exists()
                ]
                assigned_users = CompaniesTeam.objects.filter(id__in=valid_team_ids)

            document.assigned_users.set(assigned_users)
            documents.append(document)

        return documents


# class DepartmentsDocumentsCreateSerializer(serializers.ModelSerializer):
#     department_ids = serializers.ListField(
#         child=serializers.UUIDField(format='hex_verbose'), write_only=True
#     )
#     user_ids = serializers.ListField(
#         child=serializers.UUIDField(format='hex_verbose'), write_only=True , required=False
#     )
#     all = serializers.BooleanField(write_only=True, required=False, default=False)
#     schedule_time = serializers.DateTimeField(required=False, allow_null=True)
#     due_date = serializers.DateField(required=False, allow_null=True)
#     avg_completion_time = serializers.DurationField(required=False, allow_null=True)
#     overview = serializers.CharField(required=False, allow_blank=True, max_length=500)

#     class Meta:
#         model = DepartmentsDocuments
#         fields = ['id', 'name', 'file', 'department_ids', 'all', 'user_ids', 'schedule_time', 'published', 'added_by', 'created_at', 'due_date', 'avg_completion_time', 'overview']

#     def validate_department_ids(self, value):
#         # Check if all departments are active
#         for department_id in value:
#             if not Departments.objects.filter(id=department_id, is_active=True).exists():
#                 raise serializers.ValidationError({"department not found": f"Department with ID {department_id} is not active or does not exist."})
#         return value

#     def validate_team_ids(self, value):
#         # Check if all teams are active
#         for team_id in value:
#             if not CompaniesTeam.objects.filter(id=team_id, is_active=True).exists():
#                 raise serializers.ValidationError({"team not found": f"Team with ID {team_id} is not active or does not exist."})
#         return value

#     def create(self, validated_data):
#         department_ids = validated_data.pop('department_ids')
#         user_ids = validated_data.pop('user_ids', [])
#         all_users = validated_data.pop('all', False)
#         schedule_time = validated_data.pop('schedule_time', timezone.now())
#         due_date = validated_data.pop('due_date', None)
#         avg_completion_time = validated_data.pop('avg_completion_time', None)
#         overview = validated_data.pop('overview', '')
#         added_by = validated_data.pop('added_by')
#         file = validated_data.pop('file')
#         name = validated_data.pop('name')
#         published = validated_data.pop('published', False)

#         documents = []
#         for department_id in department_ids:
#             department = Departments.objects.get(id=department_id, is_active=True)
#             document = DepartmentsDocuments.objects.create(
#                 name=name,
#                 added_by=added_by,
#                 file=file,
#                 department=department,
#                 scheduled_time=schedule_time if schedule_time > timezone.now() else timezone.now(),
#                 due_date=due_date,
#                 avg_completion_time=avg_completion_time,
#                 overview=overview,
#                 published=published
#             )

#             if all_users:
#                 assigned_users = CompaniesTeam.objects.filter(departments__id=department_id)
#             else:
#                 valid_team_ids = [user_id for user_id in user_ids if CompaniesTeam.objects.filter(id=user_id, department=department, is_active=True).exists()]


class ScheduleDetailsUpdateSerializer(serializers.ModelSerializer):
    users_id = serializers.UUIDField
    department_id = serializers.UUIDField
    question_id = serializers.UUIDField
    quiz_id = serializers.UUIDField(required=False)
    document_id = serializers.UUIDField

    class Meta:
        model = ScheduleDetail
        fields = ["id", "quiz_id", "question_id", "user_id", "document_id"]

    def update(self, instance, validated_data):

        new_question_id = validated_data.pop("question_id", None)
        new_quiz_id = validated_data.pop("quiz_id", None)

        instance.question_id = new_question_id
        instance.quiz_id = new_quiz_id

        instance.save()

        return instance
