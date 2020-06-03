from crime.models import *
import json
#--
with open('crimestype.json') as file:
    ar = json.loads(file.read())

for item in ar:
    crtype = CrimeType(id=item['id'],eng_name=item["eng_name"],rus_name=item["rus_name"])
    crtype.save()
#--
with open('crime_doc.json') as file:
    ar = json.loads(file.read())

for item in ar:
    crtype_id = CrimeType.objects.get(id=item["type_id"])
    crime_doc= CrimeDoc(eng_name=item["eng_name"], rus_name=item["rus_name"],app_id=item["app_id"], type_id=crtype_id)
    crime_doc.save()
#--
with open('country_doc.json') as file:
    ar = json.loads(file.read())

for item in ar:
    countrydoc = CountryDoc(id=item["id"],eng_name=item['eng_name'], rus_name=item['rus_name'])
    countrydoc.save()
#--

with open('country_to_iso.json') as file:
    ar = json.loads(file.read())

for item in ar:
    country_iso = CountryDoc.objects.get(id=item['iso'])
    country_name= CountryNames(iso=country_iso,eng_name=item["country"])
    country_name.save()

#--

with open('socialindicator.json') as file:
    ar = json.loads(file.read())

for item in ar:
    indic= Indicator_Doc(id=item["id"], eng_name=item['eng_name'], rus_name=item["rus_name"])
    indic.save()

#--
with open('theft_2017_2018.json') as file:
    ar=json.loads(file.read())

for item in ar:
    crime_doc_id = CrimeDoc.objects.get(id=item['crime_type'])
    country_doc_id = CountryDoc.objects.get(id=item['id'])
    crime = Crimes(country_doc_id=country_doc_id,crime_doc_id=crime_doc_id, value=item['Count'], rate=float(item['Rate'].replace(',','.')), year=item['Year'])
    crime.save()
#--
with open('car_theft_2017_2018.json') as file:
    ar=json.loads(file.read())

for item in ar:
    crime_doc_id = CrimeDoc.objects.get(id=item['crime_type'])
    country_doc_id = CountryDoc.objects.get(id=item['id'])
    crime = Crimes(country_doc_id=country_doc_id,crime_doc_id=crime_doc_id, value=item['Count'], rate=float(item['Rate'].replace(',','.')), year=item['Year'])
    crime.save()

#--
with open('bulglary_2017_2018.json') as file:
    ar=json.loads(file.read())

for item in ar:
    crime_doc_id = CrimeDoc.objects.get(id=item['crime_type'])
    country_doc_id = CountryDoc.objects.get(id=item['id'])
    crime = Crimes(country_doc_id=country_doc_id,crime_doc_id=crime_doc_id, value=item['Count'], rate=float(item['Rate'].replace(',','.')), year=item['Year'])
    crime.save()