from company.models import company , AdminUser
from rest_framework import serializers
from teams.models import CompaniesTeam
from teams.api.serializers import CompaniesTeamDetailsSerializers

class AdminSerializer(serializers.ModelSerializer):
    admin = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    class Meta:
        model = AdminUser
        fields = ['id', 'admin' , 'company']
    
    def get_admin(self , obj):
        return obj.email.email
    
    def get_company(self , obj):
        return obj.company.name
    
class AdminUpdateDeleteSerializer(serializers.ModelSerializer):
    admin = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    class Meta:
        model = AdminUser
        fields = ['id' , 'admin' , 'company']
    
    def get_admin(self , obj):
        return obj.email.email
    
    def get_company(self , obj):
        return obj.company.name
    
class CompanySerializer(serializers.ModelSerializer):
    admin = serializers.SerializerMethodField(read_only=True)
    id = serializers.SerializerMethodField(read_only=True)
    # company = serializers.SerializerMethodField()
    class Meta:
        model = company
        fields = '__all__'

    def get_id(self , obj):
        return obj.id
    
    def get_admin(self, obj):
        admins = AdminUser.objects.prefetch_related('company').filter(company=obj)
        serializer = AdminSerializer(admins, many=True)
        return serializer.data
    
class CompaniesListSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    class Meta:
        model = company
        fields = ['id','name', 'logo']
        
    def get_logo(self , obj):
        if obj.logo:
            return self.context['request'].build_absolute_uri(obj.logo.url)
        return None