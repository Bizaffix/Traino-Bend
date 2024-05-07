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
    # logo = serializers.SerializerMethodField()
    class Meta:
        model = company
        fields = '__all__'

    def get_id(self , obj):
        return obj.id
    
    
    # def get_logo(self, obj):
    #     if obj.logo:
    #         return obj.logo.url
    #     else:
    #         return "/public/static/company_logos/OneColumbia.jpeg"
    # def get_logo(self, obj):
    #     request = self.context.get('request')  # Ensure 'request' is defined by getting it from the context
    #     print(obj.logo)
    #     print(obj.logo.url)
    #     if obj.logo and hasattr(obj.logo, 'url'):
    #         if request is not None:
    #             return request.build_absolute_uri(obj.logo.url)
    #     return None
    
    def get_admin(self, obj):
        admins = AdminUser.objects.prefetch_related('company').filter(company=obj)
        serializer = AdminSerializer(admins, many=True)
        return serializer.data
    
class CompaniesListSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    class Meta:
        model = company
        fields = ['name', 'logo']
        
    def get_logo(self , obj):
        if obj.logo:
            return self.context['request'].build_absolute_uri(obj.logo.url)
        return None