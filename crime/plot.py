import pandas as pd
import plotly.graph_objects as go
from crime.models import Crimes,CrimeDoc, CountryDoc, Indicators
from django.db.models.expressions import Window
from django.db.models.functions import Rank
from django.db.models import F
import requests
import json
import random
COLORS = """aqua, aquamarine, azure,
            beige, bisque, black, blanchedalmond, blue,
            blueviolet, brown, burlywood, cadetblue,
            chartreuse, chocolate, coral, cornflowerblue,
            cornsilk, crimson, cyan, darkblue, darkcyan,
            darkgoldenrod, darkgray, darkgrey, darkgreen,
            darkkhaki, darkmagenta, darkolivegreen, darkorange,
            darkorchid, darkred, darksalmon, darkseagreen,
            darkslateblue, darkslategray, darkslategrey,
            darkturquoise, darkviolet, deeppink, deepskyblue,
            dimgray, dimgrey, dodgerblue, firebrick,
            forestgreen, fuchsia, gainsboro,
            gold, goldenrod,  green,
            greenyellow, honeydew, hotpink, indianred, indigo,
            ivory, khaki, lavenderblush, lawngreen,
            lemonchiffon, lightblue, lightcoral, lightcyan,
            lightgoldenrodyellow, lightgray, lightgrey,
            lightgreen, lightpink, lightsalmon, lightseagreen,
            lightskyblue, lightslategray, lightslategrey,
            lightsteelblue, lightyellow, lime, limegreen,
            magenta, maroon, mediumaquamarine,
            mediumblue, mediumorchid, mediumpurple,
            mediumseagreen, mediumslateblue, mediumspringgreen,
            mediumturquoise, mediumvioletred, midnightblue,
            mintcream, mistyrose, moccasin, navy,
            oldlace, olive, olivedrab, orange, orangered,
            orchid, palegoldenrod, palegreen, paleturquoise,
            palevioletred, papayawhip, peachpuff, peru, pink,
            plum, powderblue, purple, red, rosybrown,
            royalblue, rebeccapurple, saddlebrown, salmon,
            sandybrown, seagreen, seashell, sienna, silver,
            skyblue, slateblue, slategray, slategrey,
            springgreen, steelblue, tan, teal, thistle, tomato,
            turquoise, violet, wheat,
            yellow, yellowgreen""".split(',')


def addNan(df, column):
    max_df = df['year'].max()
    min_df = df['year'].min()
    year = { i for i in range(min_df, max_df+1)}
    dif = year-set(df['year'])
    if dif:
        nan_df=pd.DataFrame(columns=['year',column])
        nan_df['year']=pd.Series(list(dif))
        return df.append(nan_df,ignore_index=True).sort_values(by='year')
    else:
        return df


def plotLineHistCountryCrimes(crimes,country, method):
    fig_line = go.Figure()
    fig_bar = go.Figure()
    fig_rate =go.Figure()
    for crime in crimes:
        color = random.choice(COLORS).strip()
        crimes_data = Crimes.objects.filter(crime_doc_id=crime, country_doc_id=country, is_actual=True).order_by(
            'year').values('value', 'year','rate')
        name = CrimeDoc.objects.get(id=crime).rus_name
        df = pd.DataFrame.from_records(crimes_data)
        if df.shape[0]>3:
            request_pred = requests.post('http://127.0.0.1:5000/predict', json=json.dumps(
                {'series_year': df.to_dict(orient='records'), 'method': method}))
            df_pred = json.loads(request_pred.text)
            df_pred = pd.DataFrame.from_records(df_pred)
            request_pred_rate = requests.post('http://127.0.0.1:5000/predict', json=json.dumps(
                {'series_year': df.drop(columns=['value']).rename(columns={'rate':'value'}).to_dict(orient='records'), 'method': method}))
            df_pred_rate = json.loads(request_pred_rate.text)
            df_pred_rate = pd.DataFrame.from_records(df_pred_rate)

        df = addNan(df, 'value')
        df['line_value'] = df['value']

        fig_line.add_trace(go.Scatter(x=df['year'], y=df['line_value'],
                                 mode='lines+markers', name=name.capitalize(), legendgroup=name,
                                      marker={'color':color}, line={'color':color},
                                      text="Уровень преступности: "+df['rate'].astype(str)+
                                      "<br>Количество преступлений: "+df['value'].astype(str)+"</br>"+
                                      "Год: "+df['year'].astype(str)))
        if df.shape[0]>3:
            fig_line.add_trace(go.Scatter(x=df_pred['year'], y=df_pred['value'] ,
                                          mode='lines+markers', name=name.capitalize(),
                                          marker={'symbol': "circle-open-dot", 'color': color},
                                          line={'dash': 'dot', 'color': color},
                                          showlegend=False, legendgroup=name,
                                          text="Прогнозируемый уровень преступности: "
                                               +df_pred_rate['value'].astype(str)
                                               +"<br>Прогнозируемое количество преступлений: "
                                               +df_pred['value'].astype(int).astype(str)+"</br>"+
                                               "Год: "+df_pred['year'].astype(str)))
            last_row = df.iloc[-1]
            first_row = df_pred.iloc[0]
            fig_line.add_trace(go.Scatter(x=[last_row.year, first_row.year],
                                          y=[last_row.value , first_row.value ],
                                          mode='lines', legendgroup=name, line={'color': color, 'dash': 'dot'},
                                          name=name.capitalize(),
                                          showlegend=False))

        fig_bar.add_trace(go.Bar(x=df['year'],y=df['value'], name=name.capitalize(), legendgroup=name, marker_color=color,
                                 text="Уровень преступности: "+df['rate'].astype(str)+
                                      "<br>Количество преступлений: "+df['value'].astype(str)+"</br>"+
                                      "Год: "+df['year'].astype(str)))
        if df.shape[0]>3:
            fig_bar.add_trace(go.Bar(x=df_pred['year'], y=df_pred['value'], name=name.capitalize(),
                                     showlegend=False, legendgroup=name, marker_color=color, opacity=0.5,
                                     marker_line_width=1.5,
                                     text="Прогнозируемый уровень преступности: "
                                          + df_pred_rate['value'].astype(str)
                                          + "<br>Прогнозируемое количество преступлений: "
                                          + df_pred['value'].astype(int).astype(str) + "</br>" +
                                          "Год: " + df_pred['year'].astype(str)
                                     ))

        rate_data =Crimes.objects.filter(crime_doc_id=crime,is_actual=True).annotate(rank=Window(expression=Rank(), partition_by=F('year'), order_by=F('rate').desc())).order_by('year','rank').values('country_doc_id','year','rank')
        rate_df=pd.DataFrame.from_records(rate_data)
        country_rate_df =rate_df[rate_df['country_doc_id']==country][['year','rank']]
        country_rate_df = addNan(country_rate_df,'rank')
        fig_rate.add_trace(go.Scatter(x=country_rate_df['year'],
                                      y=country_rate_df['rank'],
                                      mode='lines+markers',
                                      name=name.capitalize(),
                                      marker={'color':color},
                                      line={'color':color},
                                      text="Позиция: "+country_rate_df['rank'].astype(str)))

    fig_line.update_layout(width=1300, height=900, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(size=18,color="#000000"),
                           xaxis_title="Год", yaxis_title="Количество преступлений")
    fig_bar.update_layout(width=1200, height=800, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(size=18,color="#000000"),
                          xaxis_title="Год", yaxis_title="Количество преступлений")
    fig_rate.update_layout(width=1200, height=800, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(size=18,color="#000000"),
                          xaxis_title="Год", yaxis_title="Позиция")
    return fig_line.to_html(full_html=False, config={"displaylogo":False}), fig_bar.to_html(full_html=False, config={"displaylogo":False}), fig_rate.to_html(full_html=False, config={"displaylogo":False})


def plotHistCountriesCrime(crime, countries, method):
    fig = go.Figure()
    fig_line = go.Figure()
    fig_rate = go.Figure()
    data_rating = Crimes.objects.filter(crime_doc_id=crime, is_actual=True).annotate(rank=Window(expression=Rank(), partition_by=F('year'), order_by=F('rate').desc())).order_by('year','rank').values('country_doc_id_id','year', 'rank')
    data_rating_df=pd.DataFrame.from_records(data_rating)
    crime_name=CrimeDoc.objects.get(id=crime).rus_name
    for country in countries:
        color = random.choice(COLORS).strip()
        crimes_data = Crimes.objects.filter(crime_doc_id=crime,country_doc_id=country, is_actual=True).order_by('year').values('value','year','rate')
        name = CountryDoc.objects.get(id=country).rus_name
        df = pd.DataFrame.from_records(crimes_data)
        if df.shape[0] > 3:
            request_pred = requests.post('http://127.0.0.1:5000/predict', json=json.dumps(
                {'series_year': df.drop(columns=['value']).rename(columns={'rate':'value'}).to_dict(orient='records'), 'method': method}))
            df_pred = json.loads(request_pred.text)
            df_pred = pd.DataFrame.from_records(df_pred)
            request_pred_num = requests.post('http://127.0.0.1:5000/predict', json=json.dumps(
                {'series_year': df.to_dict(orient='records'),
                 'method': method}))
            df_pred_num = json.loads(request_pred_num.text)
            df_pred_num = pd.DataFrame.from_records(df_pred_num)

        fig_line.add_trace(go.Scatter(x=df['year'], y=df['rate'],
                                      mode='lines+markers', name=name.capitalize(), legendgroup=name,
                                      marker={'color': color}, line={'color': color},
                                      text="Количество преступлений: "+df['value'].astype(str)+
                                      "<br>Уровень преступности: "+df['rate'].astype(str)+"</br>Год: "+df['year'].astype(str)))
        if df.shape[0]>3:
            fig_line.add_trace(go.Scatter(x=df_pred['year'], y=df_pred['value'],
                                      mode='lines+markers', name=name.capitalize(),
                                      marker={'symbol': "circle-open-dot", 'color': color},
                                      line={'dash': 'dot', 'color': color},
                                      showlegend=False, legendgroup=name,
                                          text="Прогнозируемый уровень преступности: "+df_pred['value'].astype(str)
                                               +"<br>Прогнозируемое количество преступлений: "+df_pred_num['value'].astype(str)+
                                          "</br>Год: "+df_pred_num['year'].astype(str)
                                          ))
            last_row = df.iloc[-1]
            first_row = df_pred.iloc[0]
            fig_line.add_trace(go.Scatter(x=[last_row.year, first_row.year], y=[last_row.rate, first_row.value],
                       mode='lines', legendgroup=name, line={'color': color, 'dash': 'dot'}, name=name.capitalize(),
                       showlegend=False))

        fig.add_trace(go.Bar(x=df['year'], y=df['rate'], name=name, legendgroup=name, marker_color=color,
                             text="Количество преступлений: "+df['value'].astype(str)+
                             "<br>Уровень преступности: "+df['rate'].astype(str)+"</br>Год: "+df['year'].astype(str)))
        if df.shape[0] > 3:
            fig.add_trace(go.Bar(x=df_pred['year'], y=df_pred['value'], name=name.capitalize(),
                                 showlegend=False, legendgroup=name, marker_color=color, opacity=0.5,
                                 marker_line_width=1.5,
                                 text="Прогнозируемый уровень преступности: "+df_pred['value'].astype(str)
                                 +"<br>Прогнозируемое количество преступлений: "+df_pred_num['value'].astype(str)+
                                 "</br>Год: "+df_pred_num['year'].astype(str)))

        df_rate=data_rating_df[data_rating_df['country_doc_id_id']==country][['year','rank']]
        df_rate =addNan(df_rate,'rank')
        fig_rate.add_trace(go.Scatter(x=df_rate['year'], y=df_rate['rank'],
                                      mode='lines+markers', name=name.capitalize(),
                                      marker={'color': color},
                                      line={'color': color},
                                      text="Позиция: "+df_rate['rank'].astype(str)))

    fig.update_layout(width=1200, height=800, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      xaxis_title="Год", yaxis_title="Количество", font=dict(size=18,color="#000000")
                      )

    fig_line.update_layout(title_text=crime_name.capitalize(),width=1300, height=900, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                           font=dict(size=18, color="#000000"), xaxis_title="Год", yaxis_title="Количество")

    fig_rate.update_layout(width=1200, height=800, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                           xaxis_title="Год", yaxis_title="Позиция", font=dict(size=18, color="#000000"), xaxis=dict(dtick=1)
                           )
    return fig_line.to_html(full_html=False, config={"displaylogo":False}), fig.to_html(full_html=False, config={"displaylogo":False}), fig_rate.to_html(full_html=False, config={"displaylogo":False})


def plotImportance(crime, year, deloutliers, importance, featureper, objectper):
    crime_data = list(Crimes.objects.filter(crime_doc_id=crime,year=year, is_actual=True).values('value','country_doc_id'))
    indicators_data = list(Indicators.objects.filter(year=year,is_actual=True).values('value', 'country_doc_id', 'indicator_doc_id__rus_name'))
    influenceResponse = requests.post('http://127.0.0.1:5000/influence',json=json.dumps({'crime_data': crime_data,
                                                                              'indicators_data': indicators_data,
                                                                              'deloutliers': deloutliers,
                                                                              'importance': importance,
                                                                              'featureper': featureper,
                                                                              'objectper': objectper}))
    influence_data = json.loads(influenceResponse.text)
    print(influence_data)
    df = pd.DataFrame.from_records(influence_data).sort_values(by='value',ascending=False)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['name'], y=df['value'], marker={'color':df['value'].abs(),'colorscale':'Darkmint'}))
    crime_name = CrimeDoc.objects.get(id=crime).rus_name
    fig.update_layout(title_text=crime_name.capitalize(),width=1200, height=800, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=18,color="#000000"))
    return fig.to_html(full_html=False, config={"displaylogo":False}), df
