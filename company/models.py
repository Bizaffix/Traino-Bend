from accounts.models import CustomUser
from django.db import models
import uuid
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from django.urls import reverse
from PIL import Image
import os

class company(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True)
    name = models.CharField(max_length=50)
    company_id = models.CharField(max_length=50)
    logo = models.ImageField(upload_to='media/company_logos/', default="OneColumbia.jpeg", null=True, blank=True)
    country = CountryField()
    phone = PhoneNumberField()
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    fax = models.CharField(max_length=100, null=True, blank=True)
    state_or_province = models.CharField(max_length=200)
    zip_code = models.CharField(max_length=10)
    website_url = models.URLField(max_length=500 ,null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.logo:
            
            img = Image.open(self.logo)


            max_width = 500
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height))
            
            temp_file, temp_ext = os.path.splitext(self.logo.path)
            temp_file += '_temp' + temp_ext.lower()
            img.save(temp_file)

            # Save the image back to the original file path
            with open(temp_file, 'rb') as f:
                self.logo.save(os.path.basename(self.logo.name), f, save=False)

            # Delete the temporary file
            os.remove(temp_file)

        super().save(*args, **kwargs)
        
class AdminUser(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True)
    email = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='team_admin' , null=True , blank=True)
    company = models.ForeignKey(company, on_delete=models.CASCADE, related_name='company')
    is_active = models.BooleanField(default=True)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'role', 'company', 'department']

    def save(self, *args, **kwargs):
        if self.email.role != 'Admin':
            self.email.role = 'Admin'  # Set the role to 'Admin' if it's not already set
            self.email.save()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.email is not None:
            return f"{self.email.email} with role {self.email.role}"
        else:
            return "Admin Data"
        
    class Meta:
        verbose_name = ("Company Admin")
        verbose_name_plural = ("Company Admins")