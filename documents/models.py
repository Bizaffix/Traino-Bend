from django.db import models
from accounts.models import CustomUser


class UserDocuments(models.Model):
    id = models.BigAutoField(primary_key = True)
    name = models.CharField(max_length = 100)
    file = models.FileField(upload_to='documents/',)
    created_date = models.DateTimeField(auto_now_add=True)
    #user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = ("Document")
        verbose_name_plural = ("Documents")

class DocumentSummary(models.Model):
    id = models.BigAutoField(primary_key=True)
    content = models.TextField(blank=True, null=True)
    prompt_text = models.CharField(max_length = 255, blank=True, null=True)
    document = models.ForeignKey(UserDocuments, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.document.name
    
    class Meta:
        verbose_name = ("Summary")
        verbose_name_plural = ("Summary")
    
class DocumentKeyPoints(models.Model):
    id = models.BigAutoField(primary_key=True)
    content = models.TextField(blank=True, null=True)
    prompt_text = models.CharField(max_length = 255, blank=True, null=True)
    document = models.ForeignKey(UserDocuments, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.document.name
    
    class Meta:
        verbose_name = ("Keypoints")
        verbose_name_plural = ("Keypoints")

class DocumentQuiz(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length = 255)
    content = models.TextField(blank=True, null=True)
    prompt_text = models.CharField(max_length = 255, blank=True, null=True)
    document = models.ForeignKey(UserDocuments, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = ("Quiz")
        verbose_name_plural = ("Quizes")

class QuizQuestions(models.Model):
    id = models.BigAutoField(primary_key=True)
    question = models.CharField(max_length = 255, blank=True, null=True)
    option_1 = models.CharField(max_length = 255, blank=True, null=True)
    option_2 = models.CharField(max_length = 255, blank=True, null=True)
    option_3 = models.CharField(max_length = 255, blank=True, null=True)
    option_4 = models.CharField(max_length = 255, blank=True, null=True)    
    answer = models.CharField(max_length = 2, blank=True, null=True)
    quiz = models.ForeignKey(DocumentQuiz, on_delete=models.CASCADE)
    document = models.ForeignKey(UserDocuments, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question
    
    class Meta:
        verbose_name = ("Question")
        verbose_name_plural = ("Questions")