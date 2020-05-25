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
from django.http import JsonResponse
from django.template.loader import render_to_string
from crime.plot import *

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


class World(LoginRequiredMixin,View):
    login_url = '/userlogin/'

    def get(self, request):
        type_to_crimes = {}
        types = CrimeType.objects.values('id','rus_name')
        for type in types:
            type_to_crimes[type['rus_name']]=CrimeDoc.objects.filter(type_id=type['id'])
        years = Crimes.objects.values('crime_doc_id','year').distinct().order_by('crime_doc_id','-year')
        return render(request, 'world.html', {'type_to_crimes': type_to_crimes, 'years': years})

    def post(self,request):
        id=request.POST.get('crime')
        year = request.POST.get('year')
        crime = CrimeDoc.objects.get(id=id).rus_name
        query = list(Crimes.objects.filter(crime_doc_id=id, year=year, is_actual=True).values('country_doc_id__rus_name', 'country_doc_id', 'value').order_by('-value'))
        table = pd.DataFrame.from_records(query)
        table = table.rename(columns={'country_doc_id__rus_name':'страна','value':crime.capitalize(),'country_doc_id':'iso'})
        fig = go.Figure(data=go.Choropleth(
            locations=table['iso'],
            z=table[crime.capitalize()],
            text=table['страна'],
            colorscale='Greys',
            autocolorscale=False,
            reversescale=False,
            marker_line_color='darkgray',
            marker_line_width=1.5
        ))
        fig.update_layout(
            title_text=crime.capitalize(),
            width=1200,
            height=800,
            geo=dict(
                showframe=True,
                showcoastlines=False,
                projection_type='equirectangular'
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(size=18, color="#000000"),
            paper_bgcolor='rgba(0,0,0,0)'
        )
        fig_html=fig.to_html(full_html=False)
        new_string = render_to_string('map.html', {'fig':fig_html,'max_rating': query[0:5], 'min_rating': query[:-6:-1]})
        return JsonResponse({'new_string':new_string})



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
        crimes = request.POST.getlist('crime[]')
        country = request.POST.get('country')
        method = request.POST.get('predict')
        if method == 'auto':
            method = None
        if crimes and country:
            fig_line, fig_bar, fig_rate = plotLineHistCountryCrimes(crimes=crimes, country=country, method=method)
            new_string = render_to_string('countryplot.html', {'line': fig_line, 'bar': fig_bar, 'rate':fig_rate})
            return JsonResponse({'new_string': new_string})
        else:
            return JsonResponse({'new_string':''})



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
        crime = request.POST.get('crime')
        countries = request.POST.getlist('country[]')
        method = request.POST.get('predict')
        if method == 'auto':
            method = None
        if crime and countries:
            fig_line,fig, fig_rate = plotHistCountriesCrime(crime=crime, countries=countries, method=method)
            new_string = render_to_string('countriesplot.html', {'fig': fig, 'fig_rate':fig_rate, 'fig_line':fig_line})
            return JsonResponse({'new_string': new_string})
        else:
            print(1)
            return JsonResponse({'new_string':''})


class Influence(LoginRequiredMixin, View):
    login_url = '/userlogin/'

    def get(self, request):
        type_to_crimes = {}
        types = CrimeType.objects.values('id', 'rus_name')
        for type in types:
            type_to_crimes[type['rus_name']] = CrimeDoc.objects.filter(type_id=type['id'])
        years = Crimes.objects.values('crime_doc_id', 'year').distinct().order_by('crime_doc_id', '-year')
        return render(request, 'influence.html', {'type_to_crimes': type_to_crimes, 'years': years})

    def post(self, request):
        crime = request.POST.get('crime')
        year = request.POST.get('year')
        deloutliers = request.POST.get('deloutliers')
        importance = request.POST.get('importance')
        featureper = request.POST.get('featureper')
        objectper = request.POST.get('objectper')
        print(crime,year,deloutliers,importance,featureper,objectper)
        return JsonResponse({'new_string':""})

