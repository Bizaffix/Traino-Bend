from rest_framework.response import Response
from dal.autocomplete import Select2QuerySetView 
from .models import Departments, CustomCompanyUser

class CompanyAutocompleteView(Select2QuerySetView):

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return CustomCompanyUser.objects.none()

        qs = CustomCompanyUser.objects.filter(role='Admin')

        # for search or filter by email
        if self.q:
            qs = qs.filter(email__istartswith=self.q)

        return qs

class DepartmentAutocompleteView(Select2QuerySetView):

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Departments.objects.none()

        company = self.forwarded.get('company', None)
        if company:
            qs = Departments.objects.filter(company=company)
        else:
            qs = Departments.objects.none()

        # for search or filter by name
        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs
    