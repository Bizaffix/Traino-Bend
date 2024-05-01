from company.models import company
from rest_framework import serializers


class CompanySerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(read_only=True)
    company_logo = serializers.SerializerMethodField()
    class Meta:
        model = company
        fields = '__all__'

    def get_id(self , obj):
        return obj.id
    
    def get_company_logo(self , obj):
        if obj.company_logo:
            return self.context['request'].build_absolute_uri(obj.company_logo.url)
        return None
    
class CompaniesListSerializer(serializers.ModelSerializer):
    company_logo = serializers.SerializerMethodField()
    class Meta:
        model = company
        fields = ['company_name', 'company_logo']
        
    def get_company_logo(self , obj):
        if obj.company_logo:
            return self.context['request'].build_absolute_uri(obj.company_logo.url)
        return None