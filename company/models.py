from django.db import models
import uuid
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from django.urls import reverse
from PIL import Image

class company(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True)
    company_name = models.CharField(max_length=50)
    company_id = models.CharField(max_length=50)
    company_logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
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
        return self.company_name
    
    def save(self, *args, **kwargs):
        if self.company_logo:
            super().save(*args, **kwargs)

            img = Image.open(self.company_logo.path)

            # Resize the image
            desired_width = 500  # Set the desired width
            desired_height = int(img.height * (desired_width / img.width))
            resized_img = img.resize((desired_width, desired_height))


            resized_img.save(self.company_logo.path)

        super().save(*args, **kwargs)
    
    
    