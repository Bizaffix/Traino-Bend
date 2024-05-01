from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Departments, CompanyTeam, CustomCompanyUser
from django import forms
from dal.autocomplete import ModelSelect2 
import djhacker


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = '__all__'


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'

class CompanyUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomCompanyUser
        fields = '__all__'


class CompanyUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomCompanyUser
        fields = '__all__'

class CompanyTeamCreationForm(UserCreationForm):
    
    company = djhacker.formfield(
        CompanyTeam.company,
        forms.ModelChoiceField,
        widget=ModelSelect2(url='company_autocomplete')
    )

    department = djhacker.formfield(
        CompanyTeam.department,
        forms.ModelChoiceField,
        widget=ModelSelect2(url='department_autocomplete', forward=['company'])
    )

    class Meta:
        model = CompanyTeam
        fields = '__all__'


class CompanyTeamChangeForm(UserChangeForm):
    company = djhacker.formfield(
        CompanyTeam.company,
        forms.ModelChoiceField,
        widget=ModelSelect2(url='company_autocomplete')
    )

    department = djhacker.formfield(
        CompanyTeam.department,
        forms.ModelChoiceField,
        widget=ModelSelect2(url='department_autocomplete', forward=['company'])
    )
    
    class Meta:
        model = CompanyTeam
        fields = '__all__'

class DepartmentForm(forms.ModelForm):
    company = djhacker.formfield(
        Departments.company,
        forms.ModelChoiceField,
        widget=ModelSelect2(url='company_autocomplete')
    )

    
    class Meta:
        model = Departments
        fields = '__all__'