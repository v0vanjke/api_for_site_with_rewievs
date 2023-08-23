# Generated by Django 3.2 on 2023-08-22 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_genretitle'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['slug']},
        ),
        migrations.AlterModelOptions(
            name='genre',
            options={'ordering': ['slug']},
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=200, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='genre',
            name='name',
            field=models.CharField(max_length=200, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='title',
            name='description',
            field=models.TextField(blank=True, max_length=200, null=True, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='title',
            name='name',
            field=models.CharField(max_length=200, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='title',
            name='year',
            field=models.PositiveBigIntegerField(db_index=True),
        ),
        migrations.DeleteModel(
            name='GenreTitle',
        ),
    ]
