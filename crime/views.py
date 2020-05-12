from django.shortcuts import render
from django.views import View
from django.contrib.auth import authenticate, login, logout
from crime.forms import UserForm
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
import requests
import json
from crime.models import CrimeDoc, CountryNames, Crimes, CountryDoc, Indicator_Doc, Indicators,CrimeType
from django.contrib.auth.mixins import LoginRequiredMixin

class UserRegistrationView(View):
    form_class = UserForm
    def get(self, request):
        registered = False
        user_form = self.form_class()
        return render(request, 'registration.html', {'user_form': user_form, 'registered': registered})

    def post(self, request):
        user_form = self.form_class(data=request.POST)
        registered = False
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            registered = True
        else:
            user_form_new=self.form_class()
            return render(request,'registration.html',{'user_form': user_form_new, 'registered':registered, 'errors':user_form.errors, 'flag':True})
            print(user_form.errors)
        return render(request, 'registration.html', {'registered': registered})


class IndexView(View):
    def get(self, request):
        return render(request, 'index.html',)


class UserLogin(View):
    def post(self, request):
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username, password))
            return render(request,'login.html',{'invalid':True})

    def get(self, request):
        return render(request,'login.html', {})


class UserLogout(View):

    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('index'))


class Update(View):

    def get(self, request):
        crimes = CrimeDoc.objects.all()
        indicators = Indicator_Doc.objects.all()
        return render(request,'update.html',{'apps':crimes, "indics":indicators})

    def post(self, request):
        crimes_id = request.POST.getlist('types')
        if 'all' in crimes_id:
            crimes = list(CrimeDoc.objects.values('id','app_id'))
            crimes_id = [i['id'] for i in crimes]
        elif crimes_id:
            crimes = list(CrimeDoc.objects.filter(pk__in=crimes_id).values('id', 'app_id'))
        if crimes_id:
            countrys_name = list(CountryNames.objects.values('iso', 'eng_name'))
            request_app = {'crimes': crimes, 'countrys_name': countrys_name}
            response = requests.post('http://127.0.0.1:5000/update_crimes', json=json.dumps(request_app))
            json_response = json.loads(response.text)
            print(json_response)
            if json_response:
                not_actual = Crimes.objects.filter(crime_doc_id__in=crimes_id, is_actual=True)
                not_actual.update(is_actual=False)
                for item in json_response:
                    crime_doc_id = CrimeDoc.objects.only('id').get(id=item['type'])
                    country_doc_id = CountryDoc.objects.only('id').get(id=item['iso'])
                    crime = Crimes(crime_doc_id=crime_doc_id, country_doc_id = country_doc_id,
                                   value=int(float(item['value'])), year=item['year'])
                    crime.save()
        indicators_id = request.POST.getlist('indicator')
        if 'all' in indicators_id:
            indicators = list(Indicator_Doc.objects.values('id'))
            indicators_id = [i['id'] for i in indicators]
        elif indicators_id:
            indicators = list(Indicator_Doc.objects.filter(pk__in=indicators_id).values('id'))
        if indicators_id:
            request_ind = {"indicators":indicators}
            response = requests.post('http://127.0.0.1:5000/update_indicators',json=json.dumps(request_ind))
            json_response = json.loads(response.text)
            if json_response:
                not_actual = Indicators.objects.filter(indicator_doc_id__in=indicators_id, is_actual=True)
                not_actual.update(is_actual=False)
                for item in json_response:
                    indicator_doc_id=Indicator_Doc.objects.only('id').get(id=item['indicator_id'])
                    country_doc_id=CountryDoc.objects.only('id').get(id=item['id'])
                    indicator = Indicators(indicator_doc_id=indicator_doc_id, country_doc_id=country_doc_id,
                                           value=item['Value'],year=item['Year'])
                    indicator.save()
        return HttpResponseRedirect(reverse('index'))


class MainPage(View):

    def get(self, request):
        type_to_crimes = {}
        types = CrimeType.objects.values('id','rus_name')
        for type in types:
            type_to_crimes[type['rus_name']]=CrimeDoc.objects.filter(type_id=type['id'])
        years = Crimes.objects.values('crime_doc_id','year').distinct().order_by('crime_doc_id','-year')
        return render(request, 'index.html', {'type_to_crimes': type_to_crimes, 'years': years})

    def post(self,request):
        crime_ids = request.POST.getlist('crime')
        years=request.POST.getlist('year')
        print(crime_ids, years)
        return HttpResponseRedirect(reverse('index'))


class OneCountry(LoginRequiredMixin,View):
    login_url = '/userlogin/'

    def get(self, request):
        countries = CountryDoc.objects.filter(crimes__crime_doc_id__isnull=False).values().distinct()
        type_to_crimes = {}
        types = CrimeType.objects.values('id', 'rus_name')
        for type in types:
            type_to_crimes[type['rus_name']] = CrimeDoc.objects.filter(type_id=type['id']).values('id','rus_name','crimes__country_doc_id').distinct()
        return render(request,'onecountry.html',{'countries':countries,'type_to_crimes':type_to_crimes})

    def post(self, request):
        country_id = request.POST.get('country')
        crime_ids = request.POST.getlist('crime')
        print(country_id,crime_ids)
        return HttpResponseRedirect(reverse('index'))



class CompareCountries(LoginRequiredMixin, View):
    login_url = '/userlogin/'

    def get(self, request):
        type_to_crimes = {}
        types = CrimeType.objects.values('id', 'rus_name')
        for type in types:
            type_to_crimes[type['rus_name']] = CrimeDoc.objects.filter(type_id=type['id'])
        countries = CountryDoc.objects.filter(crimes__crime_doc_id__isnull=False).values('id','rus_name','crimes__crime_doc_id').distinct()
        return render(request,'compare.html',{'type_to_crimes':type_to_crimes,'countries':countries})

    def post(self, request):
        crime_id = request.POST.get('crime')
        countries_id = request.POST.getlist('country')
        print(crime_id,countries_id)
        return HttpResponseRedirect(reverse('index'))

