import pandas as pd
import plotly.graph_objects as go
from crime.models import Crimes,CrimeDoc, CountryDoc

def plotLineHistCountryCrimes(crimes,country):
    fig_line = go.Figure()
    fig_bar = go.Figure()
    for crime in crimes:
        crimes_data = Crimes.objects.filter(crime_doc_id=crime, country_doc_id=country, is_actual=True).order_by(
            'year').values('value', 'year')
        name = CrimeDoc.objects.get(id=crime).rus_name
        df = pd.DataFrame.from_records(crimes_data)
        max_value = df['value'].max()
        df['line_value'] = df['value'] / max_value
        fig_line.add_trace(go.Scatter(x=df['year'], y=df['line_value'],
                                 mode='lines+markers',
                                 name=name))
        fig_bar.add_trace(go.Bar(x=df['year'],y=df['value'], name=name))
    fig_line.update_layout(width=1200, height=800)
    fig_bar.update_layout(width=1200, height=800)
    return fig_line.to_html(full_html=False), fig_bar.to_html(full_html=False)

def plotHistCountriesCrime(crime, countries):
    fig = go.Figure()
    for country in countries:
        crimes_data = Crimes.objects.filter(crime_doc_id=crime,country_doc_id=country, is_actual=True).order_by('year').values('value','year')
        name = CountryDoc.objects.get(id=country).rus_name
        df = pd.DataFrame.from_records(crimes_data)
        fig.add_trace(go.Bar(x=df['year'], y=df['value'], name=name))
    fig.update_layout(width=1200, height=800)
    return fig.to_html(full_html=False)


