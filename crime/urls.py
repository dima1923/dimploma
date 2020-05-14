from django.conf.urls import url
from crime.views import UserRegistrationView, UserLogin, UserLogout,Update,OneCountry,CompareCountries,World,Map,OneCountryPlot
# SET THE NAMESPACE!
app_name = 'crime'
# Be careful setting the name to just /login use userlogin instead!
urlpatterns=[
    url(r'^register/$', UserRegistrationView.as_view(), name='register'),
    url(r'^userlogin/$', UserLogin.as_view(), name='userlogin'),
    url(r'^logout/$', UserLogout.as_view(), name='logout'),
    url(r'^update/$', Update.as_view(),name='update'),
    url(r'^onecountry/$',OneCountry.as_view(),name='onecountry'),
    url(r'^compare/$',CompareCountries.as_view(),name='compare'),
    url(r'^world/$',World.as_view(), name='world'),
    url(r'^map/$',Map.as_view(), name='map'),
    url(r'cplot/$',OneCountryPlot.as_view(), name='cplot')
]