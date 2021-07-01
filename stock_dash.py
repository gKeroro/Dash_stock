import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Output, Input, State
import requests
from bs4 import BeautifulSoup
import pandas as pd
import pandas_datareader as pdr

def update_news():
    r = requests.get('https://news.cnyes.com/news/cat/tw_stock')
    soup=BeautifulSoup(r.text, 'html.parser')
    test = soup.find_all("a", {"class": "_1Zdp"})
    df= pd.DataFrame()
    headline =[]
    url = []
    for news in test[:10]:
        headline.append(news.text)
        url.append("https://news.cnyes.com"+news.get('href'))
    df['headline'] =headline
    df['url']=url
    return df

def generate_html_table(max_rows=10):

    df = update_news()

    return html.Div(
        [
            html.Div(
                html.Table(
                    # Header
                    [html.Tr([html.Th()])]
                    +
                    # Body
                    [
                        html.Tr(
                            [
                                html.Td(
                                    html.A(
                                        df.iloc[i]["headline"],
                                        href=df.iloc[i]["url"],
                                        target="_blank"
                                    )
                                )
                            ]
                        )
                        for i in range(min(len(df),max_rows))
                    ]
                ),
                style={"height": "300px", "overflowY": "scroll"},
            ),
        ],
        style={"height": "100%"},)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app =dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout =html.Div([

    html.Div([
        html.H2("Stock App"),
        html.Img(src="https://image.flaticon.com/icons/png/512/4256/4256900.png")
    ], className="banner"),

     html.Div([
        dcc.Input(id="stock-input", value="2609", type="text"),
        html.Button(id="submit-button", n_clicks=0, children ="submit") 
    ]),

    html.Div([
        html.Div([
            dcc.Graph(
                id="graph_close",
            )
        ],className="six columns"),

         html.Div([
            html.H3("Market News"),
            generate_html_table()
        ], className="six columns"),

    ],className="row")
])

@app.callback(Output('graph_close', 'figure'),
              [Input("submit-button", "n_clicks")] , 
              [State("stock-input", "value")])

def update_fig(n_clicks,inputstock):

    inputstock = inputstock+".TW"
    df = pdr.DataReader(inputstock, 'yahoo')
    df = df.reset_index()

   
    trace_line = go.Scatter(x=df.Date,
                            y=df.Close,
                            name='Close',
                            line = dict(color="#DF3F3F"))

    trace_candle = go.Candlestick(x=df.Date,
                           open=df.Open,
                           high=df.High,
                           low=df.Low,
                           close=df.Close,
                           increasing_line_color= '#DF3F3F', 
                           decreasing_line_color= '#338A49',
                           visible=False,
                           showlegend=False)

    trace_bar = go.Ohlc(x=df.Date,
                           open=df.Open,
                           high=df.High,
                           low=df.Low,
                           close=df.Close,
                           increasing_line_color= '#DF3F3F', 
                           decreasing_line_color= '#338A49',
                           visible=False,
                           showlegend=False)

    data = [trace_line, trace_candle, trace_bar]
   

    updatemenus = list([
        dict(
            buttons=list([
                dict(
                    args=[{'visible': [True, False, False]}],
                    label='Line',
                    method='update'
                ),
                dict(
                    args=[{'visible': [False, True, False]}],
                    label='Candle',
                    method='update'
                ),
                dict(
                    args=[{'visible': [False, False, True]}],
                    label='Bar',
                    method='update'
                ),
            ]),
            direction='down',
            pad={'r': 10, 't': 10},
            showactive=True,
            x=0,
            xanchor='left',
            y=1.05,
            yanchor='top'
        ),
    ])

    layout = dict(
        title=inputstock,
        updatemenus=updatemenus,
        autosize=False,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label='1m',
                         step='month',
                         stepmode='backward'),
                    dict(count=6,
                         label='6m',
                         step='month',
                         stepmode='backward'),
                    dict(count=1,
                         label='YTD',
                         step='year',
                         stepmode='todate'),
                    dict(count=1,
                         label='1y',
                         step='year',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type='date'
        )
    )

    return {
        "data":data,
        "layout":layout
    }

if __name__ == '__main__':
    app.run_server(debug=True)