# Generated by Django 3.2 on 2022-08-15 08:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tagsrecipe',
            old_name='tag',
            new_name='tags',
        ),
    ]
