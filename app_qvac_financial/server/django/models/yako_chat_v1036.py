from django.db import models
from app_qvac_financial.server.django.models.authentication import QVACWebCredential

class YakoWebConversation(models.Model):
    owner = models.ForeignKey(QVACWebCredential, on_delete=models.CASCADE, related_name='yako_web_conversations')
    title = models.CharField(max_length=160)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        app_label = 'app_qvac_financial'
        ordering = ['-id']

class YakoWebMessage(models.Model):
    conversation = models.ForeignKey(YakoWebConversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=12)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        app_label = 'app_qvac_financial'
        ordering = ['id']
