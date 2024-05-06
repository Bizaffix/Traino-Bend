from company.models import company , AdminUser
from rest_framework import serializers

class AdminSerializer(serializers.ModelSerializer):
    admin = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    class Meta:
        model = AdminUser
        fields = ['id', 'admin' , 'company']
    
    def get_admin(self , obj):
        return obj.admin.email
    
    def get_company(self , obj):
        return obj.company.company_name
    
class AdminUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = ['admin' , 'company']
    
class CompanySerializer(serializers.ModelSerializer):
    admin = serializers.SerializerMethodField(read_only=True)
    id = serializers.SerializerMethodField(read_only=True)
    company_logo = serializers.SerializerMethodField()
    class Meta:
        model = company
        fields = '__all__'

    def get_id(self , obj):
        return obj.id
    
    def get_company_logo(self , obj):
        if obj.company_logo is not None:
            return self.context['request'].build_absolute_uri(obj.company_logo.url)
        return None
    
    def get_admin(self, obj):
        admins = AdminUser.objects.prefetch_related('company').filter(company=obj)
        serializer = AdminSerializer(admins, many=True)
        return serializer.data
    
class CompaniesListSerializer(serializers.ModelSerializer):
    company_logo = serializers.SerializerMethodField()
    class Meta:
        model = company
        fields = ['company_name', 'company_logo']
        
    def get_company_logo(self , obj):
        if obj.company_logo:
            return self.context['request'].build_absolute_uri(obj.company_logo.url)
        return None