# 職缺分析版面
# 匯入套件
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

# 前端版面呈現
jobSearchLayout = html.Div([

    html.Center(html.H1('職缺爬蟲')),

    # 職缺爬蟲設定關鍵字搜尋處
    dbc.Row([
        dbc.Col([html.Span('請輸入要爬蟲的關鍵字：'),
                 dcc.Input(id='searchKeyword', value='', type='text', size=40)])]),

    dbc.Row([
        dbc.Col([html.Span('請輸入最大爬取頁數：'),
                 dcc.Input(id='searchMaxPage', value=3, type='number', min=1, max=10)])
    ]),

    dbc.Row([
        dbc.Col(html.Button(id='submitButtonSearch', children='查詢'))
    ]),

    # 爬蟲訊息提示處
    dbc.Row([
        dbc.Col([
            # 紀錄本次使用者查詢log的ID
            html.Div(id='searchLogFileName', style={'display': 'none'}),
            # 提醒使用者結果訊息
            dbc.Spinner(html.Center(html.P(id='searchStatus')), color="primary")
        ])
    ]),

    html.Hr(),

    # 定時執行取出爬蟲log紀錄
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Span('爬蟲程式執行狀態'),
                dcc.Textarea(
                    id='logUpdateText',
                    value='',
                    style={'width': '100%', 'height': 300},
                ),
                dcc.Interval(id='searchLogInterval', interval=1 * 1000, n_intervals=0)
            ])
        ])
    ])
])
