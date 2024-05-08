from rest_framework import serializers
from teams.models import CompaniesTeam
from api.serializers import UserCreateSerializer
from accounts.models import CustomUser


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'password')

class CompaniesTeamSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CompaniesTeam
        fields = ['id', 'members', 'company']

    def get_id(self , obj):
        return obj.id
        
class CompaniesTeamDetailsSerializers(serializers.ModelSerializer):
    member_email = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    class Meta:
        model = CompaniesTeam
        fields = "__all__"
        
    def get_member_email(self , obj):
        return obj.members.email
    
    def get_company(self , obj):
        return obj.company.name
        