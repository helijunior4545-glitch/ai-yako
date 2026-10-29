from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [('app_qvac_financial', '0001_initial')]
    operations = [
        migrations.CreateModel(name='YakoWebConversation', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('title', models.CharField(max_length=160)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='yako_web_conversations', to='app_qvac_financial.qvacwebcredential')),
        ], options={'ordering':['-id']}),
        migrations.CreateModel(name='YakoWebMessage', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('role', models.CharField(max_length=12)),
            ('content', models.TextField()),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='app_qvac_financial.yakowebconversation')),
        ], options={'ordering':['id']}),
    ]
