# Generated by Django 3.0.5 on 2020-05-11 15:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CountryDoc',
            fields=[
                ('id', models.CharField(max_length=5, primary_key=True, serialize=False)),
                ('eng_name', models.CharField(max_length=150)),
                ('rus_name', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='CrimeDoc',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('eng_name', models.CharField(max_length=150)),
                ('rus_name', models.CharField(max_length=150)),
                ('app_id', models.CharField(max_length=200, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='CrimeType',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('eng_name', models.CharField(max_length=200)),
                ('rus_name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Indicator_Doc',
            fields=[
                ('id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('eng_name', models.CharField(max_length=150)),
                ('rus_name', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Indicators',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('value', models.FloatField()),
                ('year', models.IntegerField()),
                ('is_actual', models.BooleanField(default=True)),
                ('country_doc_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crime.CountryDoc')),
                ('indicator_doc_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crime.Indicator_Doc')),
            ],
        ),
        migrations.CreateModel(
            name='Crimes',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('value', models.IntegerField()),
                ('year', models.IntegerField()),
                ('is_actual', models.BooleanField(default=True)),
                ('country_doc_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crime.CountryDoc')),
                ('crime_doc_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crime.CrimeDoc')),
            ],
        ),
        migrations.AddField(
            model_name='crimedoc',
            name='type_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crime.CrimeType'),
        ),
        migrations.CreateModel(
            name='CountryNames',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('eng_name', models.CharField(max_length=150)),
                ('iso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crime.CountryDoc')),
            ],
        ),
    ]