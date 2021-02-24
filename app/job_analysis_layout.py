# 職缺分析版面
# 匯入套件
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

# 前端版面呈現
jobAnalysisLayout = html.Div([

    html.Center(html.H1('職缺分析')),

    # 職缺分析結果搜尋處
    dbc.Row([
        dbc.Col([html.Span('請選取想要分析的職缺：'),
                 html.Span('(選項正在準備中 請稍等...)', id='analysisDropdownPrep'),
                 dbc.Spinner(dcc.Dropdown(id='analysisTarget'), color="primary")]),
        dbc.Col(html.Button(id='submitButtonAnalysis', children='查詢', style={'marginTop': 25}))
    ]),
    html.Hr(),

    # 查詢資料標題
    dbc.Row([
        dbc.Col([
            html.Center(html.H1(id='title')),
            html.Center(html.H3(id='dataDownloadTime'))
        ])
    ]),

    # 樣本統計資訊
    dbc.Row([
        dbc.Col(dbc.Spinner(html.Div(id='sampleInfo'), color="primary"))
    ]),
    html.Hr(),

    dbc.Row([
        # 前10名最需要此職缺的產業長條圖
        dbc.Col(dbc.Spinner(dcc.Graph(id='companyIndustryFig'), color="primary"), md=6),
        # 前10名職缺所屬的職業類別
        dbc.Col(dbc.Spinner(dcc.Graph(id='categoryFig'), color="primary"), md=6)
    ]),
    html.Hr(),

    dbc.Row([
        # 薪情最好前10名職業類別
        dbc.Col(dbc.Spinner(dcc.Graph(id='catAndSalFig'), color="primary"), md=6),
        # 職缺地點前10名
        dbc.Col(dbc.Spinner(dcc.Graph(id='locationFig'), color="primary"), md=6)
    ]),
    html.Hr(),

    dbc.Row([
        # 職缺年資要求
        dbc.Col(dbc.Spinner(dcc.Graph(id='rqYearFig'), color="primary"), md=6),
        # 職缺學歷要求
        dbc.Col(dbc.Spinner(dcc.Graph(id='rqEducationFig'), color="primary"), md=6)
    ]),
    html.Hr(),

    dbc.Row([
        # 前10名職缺科系要求
        dbc.Col(dbc.Spinner(dcc.Graph(id='rqDeptFig'), color="primary"), md=6),
        # 前15名職缺技能要求
        dbc.Col(dbc.Spinner(dcc.Graph(id='specialtyFig'), color="primary"), md=6)
    ]),
    html.Hr(),

    # 職缺其他條件文字雲
    dbc.Row([
        dbc.Col([
            html.Center(html.H3('職缺其他條件-文字雲')),
            html.Center(html.P('職缺其他條件為企業額外撰寫的職缺資訊，通常會對工作進行更多描述。此處採用結巴套件來進行斷詞，'
                               '並繪製文字雲來觀察此職缺的重要關鍵字詞。'))])
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Spinner(html.Center(html.Img(id="cloudTextFig", height='60%', width='60%')), color="primary"),
            align="center")
    ])
])
