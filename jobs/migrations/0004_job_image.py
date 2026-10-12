from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0003_alter_job_options_job_salary_period'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='image',
            field=models.ImageField(blank=True, help_text='Main job image/banner shown on the public job page and card.', upload_to='public_uploads/jobs/'),
        ),
    ]
