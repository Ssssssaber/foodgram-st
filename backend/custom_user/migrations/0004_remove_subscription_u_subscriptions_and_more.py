# Generated by Django 5.1.7 on 2025-04-01 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_user', '0003_remove_subscription_u_subscriptions_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='subscription',
            name='u_subscriptions',
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.UniqueConstraint(
                fields=('user', 'target'),
                name='u_subscriptions'
            ),
        ),
    ]
