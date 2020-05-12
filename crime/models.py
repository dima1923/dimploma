from django.db import models


class CrimeType(models.Model):
    id = models.IntegerField(primary_key=True)
    eng_name = models.CharField(max_length=200)
    rus_name = models.CharField(max_length=200)


class CrimeDoc(models.Model):
    id = models.AutoField(primary_key=True)
    eng_name = models.CharField(max_length=150)
    rus_name = models.CharField(max_length=150)
    app_id = models.CharField(unique=True, max_length=200)
    type_id = models.ForeignKey('CrimeType', unique=False, on_delete=models.CASCADE)


class CountryDoc(models.Model):
    id = models.CharField(primary_key=True, max_length=5)
    eng_name = models.CharField(max_length=150)
    rus_name = models.CharField(max_length=150)


class CountryNames(models.Model):
    id = models.AutoField(primary_key=True)
    iso = models.ForeignKey('CountryDoc',on_delete=models.CASCADE)
    eng_name = models.CharField(max_length=150)


class Crimes(models.Model):
    id = models.AutoField(primary_key=True)
    crime_doc_id = models.ForeignKey('CrimeDoc',unique=False, on_delete=models.CASCADE)
    country_doc_id = models.ForeignKey('CountryDoc', unique=False, on_delete=models.CASCADE)
    value = models.IntegerField()
    year = models.IntegerField()
    is_actual = models.BooleanField(default=True)


class Indicator_Doc(models.Model):
    id = models.CharField(primary_key=True, max_length=30)
    eng_name = models.CharField(max_length=150)
    rus_name = models.CharField(max_length=150)


class Indicators(models.Model):
    id = models.AutoField(primary_key=True)
    country_doc_id = models.ForeignKey('CountryDoc',on_delete=models.CASCADE)
    indicator_doc_id = models.ForeignKey('Indicator_Doc',on_delete=models.CASCADE)
    value = models.FloatField()
    year = models.IntegerField()
    is_actual = models.BooleanField(default=True)
