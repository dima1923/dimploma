import pandas as pd
import plotly.graph_objects as go
from crime.models import Crimes,CrimeDoc, CountryDoc
from django.db.models.expressions import Window
from django.db.models.functions import Rank
from django.db.models import F


def addNan(df, column):
    max_df=df['year'].max()
    min_df=df['year'].min()
    year={ i for i in range(min_df, max_df+1)}
    dif=year-set(df['year'])
    if dif:
        nan_df=pd.DataFrame(columns=['year',column])
        nan_df['year']=pd.Series(list(dif))
        return df.append(nan_df,ignore_index=True).sort_values(by='year')
    else:
        return df


def plotLineHistCountryCrimes(crimes,country):
    fig_line = go.Figure()
    fig_bar = go.Figure()
    fig_rate =go.Figure()
    for crime in crimes:
        crimes_data = Crimes.objects.filter(crime_doc_id=crime, country_doc_id=country, is_actual=True).order_by(
            'year').values('value', 'year')
        name = CrimeDoc.objects.get(id=crime).rus_name
        df = pd.DataFrame.from_records(crimes_data)
        df = addNan(df, 'value')
        max_value = df['value'].max()
        df['line_value'] = df['value'] / max_value
        fig_line.add_trace(go.Scatter(x=df['year'], y=df['line_value'],
                                 mode='lines+markers', name=name.capitalize()))
        fig_bar.add_trace(go.Bar(x=df['year'],y=df['value'], name=name.capitalize()))
        rate_data =Crimes.objects.filter(crime_doc_id=crime,is_actual=True).annotate(rank=Window(expression=Rank(), partition_by=F('year'), order_by=F('value').desc())).order_by('year','rank').values('country_doc_id','year','rank')
        rate_df=pd.DataFrame.from_records(rate_data)
        country_rate_df =rate_df[rate_df['country_doc_id']==country][['year','rank']]
        country_rate_df = addNan(country_rate_df,'rank')
        fig_rate.add_trace(go.Scatter(x=country_rate_df['year'], y=country_rate_df['rank'], mode='lines+markers',name=name.capitalize()))
    fig_line.update_layout(width=1300, height=900, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(size=18,color="#000000"))
    fig_bar.update_layout(width=1200, height=800, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(size=18,color="#000000"),
                          xaxis_title="Год", yaxis_title="Количество")
    fig_rate.update_layout(width=1200, height=800, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(size=18,color="#000000"),
                          xaxis_title="Год", yaxis_title="Позиция")
    return fig_line.to_html(full_html=False, config={"displaylogo":False}), fig_bar.to_html(full_html=False, config={"displaylogo":False}), fig_rate.to_html(full_html=False, config={"displaylogo":False})


def plotHistCountriesCrime(crime, countries):
    fig = go.Figure()
    fig_rate = go.Figure()
    data_rating = Crimes.objects.filter(crime_doc_id=crime, is_actual=True).annotate(rank=Window(expression=Rank(), partition_by=F('year'), order_by=F('value').desc())).order_by('year','rank').values('country_doc_id_id','year', 'rank')
    data_rating_df=pd.DataFrame.from_records(data_rating)
    crime_name=CrimeDoc.objects.get(id=crime).rus_name
    for country in countries:
        crimes_data = Crimes.objects.filter(crime_doc_id=crime,country_doc_id=country, is_actual=True).order_by('year').values('value','year')
        name = CountryDoc.objects.get(id=country).rus_name
        df = pd.DataFrame.from_records(crimes_data)
        fig.add_trace(go.Bar(x=df['year'], y=df['value'], name=name))
        df_rate=data_rating_df[data_rating_df['country_doc_id_id']==country][['year','rank']]
        df_rate =addNan(df_rate,'rank')
        fig_rate.add_trace(go.Scatter(x=df_rate['year'], y=df_rate['rank'],
                                      mode='lines+markers', name=name.capitalize()))
    fig.update_layout(title_text=crime_name.capitalize(),width=1200, height=800, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      xaxis_title="Год", yaxis_title="Количество", font=dict(size=18,color="#000000")
                      )
    fig_rate.update_layout(title_text="Изменение позиции страны в рейтинге",width=1200, height=800, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                           xaxis_title="Год", yaxis_title="Позиция", font=dict(size=18, color="#000000"), xaxis=dict(dtick=1)
                           )
    return fig.to_html(full_html=False, config={"displaylogo":False}), fig_rate.to_html(full_html=False, config={"displaylogo":False})


