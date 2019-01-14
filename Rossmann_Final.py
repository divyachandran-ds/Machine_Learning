import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import feather 
from scipy import stats

app = dash.Dash()

# Boostrap CSS.
app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})  # noqa: E501

PATH = '../python/dataset/'
print (PATH)
df = feather.read_dataframe(f'{PATH}joined')
#df_store = df.groupby(['Store'],as_index =False).agg({'CompetitionDistance': 'max','StoreType':'min','State':'min','Assortment': 'min','Sales': 'mean'})
df_store_main = df.groupby(['Store'],as_index = False).agg({'CompetitionDistance': 'max','StoreType':'min','Assortment': 'min','Sales': 'mean'})
df_store = df.groupby(['Store','Promo'],as_index = False).agg({'CompetitionDistance': 'max','StoreType':'min','Assortment': 'min','Sales': 'mean'})
df_store_main = df_store_main[df_store_main['CompetitionDistance'] <=30000]
df_store = df_store[df_store['CompetitionDistance'] <=30000]

app.layout = html.Div([
    html.Div([
        html.Div(
            [
                html.H1(children='Rossmann Stores Sales',
                        style={
                                'textAlign': 'center',"text-transform": 'uppercase'
                                },
                        className='twelve columns'),
              
                html.Div(children='''
                        Rossmann operates over 1,115 drug stores across Germany.
                        Average sales over a 2.5 year time period along with nearest competitor distance
                        categorized by store type is shown below.
                         

                        ''',
                        style={
                                'textAlign': 'center',
                                },
                        className='eight columns offset-by-two'
                )
            ], className="row"
        ),
        html.Div(
            [
            dcc.Graph(
         id='mainScatterplot',
        
                )
            ],className="ten columns offset-by-one"),
            html.Div(
            [
             html.Div([       
            dcc.RangeSlider(
                id='distSlider',
                min=df_store['CompetitionDistance'].min(),
                max=df_store['CompetitionDistance'].max(),
                value= [0,5000],
                marks={
                        0: '0',
                        1000: '1000',
                        5000: '5000',
                        10000: '10000',
                        15000: '15000',
                        20000: '20000',
                        25000: '25000',
                        30000: '30000'
                    })
                ],className='ten columns offset-by-one')
            ],className="row"),    
    
        html.Div(["Promotion has a significant impact on sales"],
                 style={'margin-top': '40', 'textAlign': 'center',"font-size": "30px"},className="row"),
        html.Div([],className="row"),
        html.Div(
            [
                
                html.Div(
                    [
                        html.P('Store Type:'),
                        dcc.RadioItems(
                                id = 'storeType_1',
                                options=[{'label': i, 'value': i} for i in ['a', 'b','c','d']],
                                value='a',
                                labelStyle={'display': 'inline-block'}
                        ),
                    ],
                    className='"row"',
                    style={'margin-top': '20', 'textAlign': 'center',"font-size": "15px"}
                )
                
                
            ], className="row"
        ),
        
        html.Div(
            [
            html.Div([
                dcc.Graph(
                    id='scatterPlot_1',
                    config={
                            'displayModeBar':False},
                )
                ],style={"automargin":True}, className= 'six columns'
                ),

            html.Div([
                dcc.Graph(
                    id='scatterPlot_2',
                    config={
                            'displayModeBar':False},
                )
                ],style={"automargin":True}, className= 'six columns'
                )
            ], className="row"
        ),
        
        
    ] )
  
])
            
@app.callback(
    dash.dependencies.Output('mainScatterplot', 'figure'),
    [dash.dependencies.Input('distSlider', 'value'),
     ])          
def update_figure(distSlider_val):
    #distSLider returns a list with two numbers   
    filtered_df = df_store_main[(df_store_main['CompetitionDistance'] >=distSlider_val[0]) & (df_store_main['CompetitionDistance'] <=distSlider_val[1])] 

    trace1 = [go.Scatter(
            
        x= filtered_df[filtered_df['StoreType'] == StoreType]['CompetitionDistance'],
        y= filtered_df[filtered_df['StoreType'] == StoreType]['Sales'],
        text= filtered_df['StoreType'],
        mode='markers',
        opacity=0.7,
        marker={
            'size': 10,
            'line': {'width': 0.5, 'color': 'white'}
        },
        name = StoreType
        
    )for StoreType in ['a', 'b', 'c','d']
    ]
      
    return {
        'data': trace1,
        'layout': go.Layout(
                
            xaxis=dict(
                    showticklabels=False
            #{'title': 'Competition Distance'},
            ),
            yaxis= dict(
                range = [0, 30000],
                title='Average Sales ($)',
                #titlefont=dict(
                #family='Courier New, monospace',
                #size=20,
                #color='#7f7f7f'
            #)
            ),
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            #showlegend=False,
            legend=dict(x=0.9, y=0.9),
            
            hovermode='closest'
        )
    }       

@app.callback(
    dash.dependencies.Output('scatterPlot_1', 'figure'),
    [dash.dependencies.Input('distSlider', 'value'),
     dash.dependencies.Input('storeType_1', 'value')])

def update_figure(distSlider_val,storeType_val):
    
    df_store_promo = df_store[df_store['Promo'] == 0]
    filtered_df = df_store_promo[(df_store_promo['CompetitionDistance'] >=distSlider_val[0]) & (df_store_promo['CompetitionDistance'] <=distSlider_val[1])]
    

    traces = []

    trace1 = (go.Scatter(
            
        x= filtered_df[filtered_df['StoreType'] == storeType_val[0]]['CompetitionDistance'],
        y= filtered_df[filtered_df['StoreType'] == storeType_val[0]]['Sales'],
        #text= filtered_df['StoreType'],
        mode='markers',
        opacity=0.7,
        marker={
            'size': 10,
            'line': {'width': 0.5, 'color': 'white'}
        },
        
    ))
    # Trend line using linear regression
    x = filtered_df[filtered_df['StoreType'] == storeType_val[0]]['CompetitionDistance']
    y = filtered_df[filtered_df['StoreType'] == storeType_val[0]]['Sales']
    # Linear Regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
    # Equation of a line
    line = slope*x+intercept
    trace2 = (go.Scatter(
        x=x,
        y=line,
        mode='lines',
        marker=go.Marker(color='red'),
        
    ))
    traces = [trace1, trace2]
    return {
        'data': traces,
        'layout': go.Layout(
            xaxis=dict(
                    showticklabels=False
            #{'title': 'Competition Distance'},
            ),
            yaxis= dict(
                range = [0, 30000],
                title='Average Sales ($)',
                #itlefont=dict(
                #family='Courier New, monospace',
                #size=20,
                #color='#7f7f7f'
            #)
            ),
            margin={'l': 40, 'b': 40, 't': 40, 'r': 40},
            showlegend=False,
            title='Sales without Promotion',
                    
            hovermode='closest'
        )
    }

@app.callback(
    dash.dependencies.Output('scatterPlot_2', 'figure'),
    [dash.dependencies.Input('distSlider', 'value'),
     dash.dependencies.Input('storeType_1', 'value')])

def update_figure(distSlider_val, storeType_val):
    
    df_store_promo = df_store[df_store['Promo'] == 1]
    filtered_df = df_store_promo[(df_store_promo['CompetitionDistance'] >=distSlider_val[0]) & (df_store_promo['CompetitionDistance'] <=distSlider_val[1])]
    

    traces = []

    trace1 = (go.Scatter(
            
        x= filtered_df[filtered_df['StoreType'] == storeType_val[0]]['CompetitionDistance'],
        y= filtered_df[filtered_df['StoreType'] == storeType_val[0]]['Sales'],
        #text= filtered_df['StoreType'],
        mode='markers',
        opacity=0.7,
        marker={
            'size': 10,
            'line': {'width': 0.5, 'color': 'white'}
        },
        name='a'
    ))
    # Trend line using linear regression
    x = filtered_df[filtered_df['StoreType'] == storeType_val[0]]['CompetitionDistance']
    y = filtered_df[filtered_df['StoreType'] == storeType_val[0]]['Sales']
    # Linear Regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
    # Equation of line
    line = slope*x+intercept
    trace2 = (go.Scatter(
        x=x,
        y=line,
        mode='lines',
        marker=go.Marker(color='red'),
        name='Fit'
    ))
    traces = [trace1, trace2]
    return {
        'data': traces,
        'layout': go.Layout(
            xaxis=dict(
                    showticklabels=False
            #{'title': 'Competition Distance'},
            ),
            yaxis= dict(
                range = [0, 30000],
                title='Average Sales ($)',
                #titlefont=dict(
                #family='Courier New, monospace',
                #size=20,
                #color='#7f7f7f'
            #)
            ),
            margin={'l': 40, 'b': 40, 't': 40, 'r': 40},
            showlegend=False,
            title='Sales with Promotion',
            
            hovermode='closest'
        )
    }
if __name__ == '__main__':
    app.run_server(debug=True)


