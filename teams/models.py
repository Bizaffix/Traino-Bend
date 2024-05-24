from django.db import models
import uuid
from company.models import company
from accounts.models import CustomUser

class CompaniesTeam(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True)
    members = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='team_member' , null=True, blank=True)
    company = models.ForeignKey(company, on_delete=models.CASCADE, related_name='company_teams')
    is_active = models.BooleanField(default=True)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'role', 'company', 'department']

    # def save(self, *args, **kwargs):
    #     if not self.members.role == 'User':
    #         self.members.role = 'User'  # Set the role to 'User' if it's not already set
    #         self.members.save()  # Save the associated to User
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.members.email} with role {self.members.role}"
    
    class Meta:
        verbose_name = ("Company Team Member")
        verbose_name_plural = ("Company Team Members")