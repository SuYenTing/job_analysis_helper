# 首頁版面
# 匯入套件
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# 匯入自定義程式碼
from app import app
from job_analysis_layout import jobAnalysisLayout
from job_search_layout import jobSearchLayout
import callbacks

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

# 側邊選單
sidebar = html.Div(
    [
        html.H3("職缺分析小幫手"),
        html.Hr(),
        html.P(
            "", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("職缺分析", id='jobAnalysisPage', href="/job_analysis", active="exact"),
                dbc.NavLink("職缺爬蟲", id='jobSearchPage', href="/job_search", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

# 主內容畫面
content = html.Div(id="page-content", style=CONTENT_STYLE)

# 整合側邊選單與主內容畫面
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


# 選單對應操作
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return html.P("您好，若想要觀看職缺分析結果，請點選「職缺分析」頁面。若想要分析新的職缺資訊，請點選「職缺爬蟲」頁面，重新下載資料。")
    elif pathname == "/job_analysis":
        return jobAnalysisLayout
    elif pathname == "/job_search":
        return jobSearchLayout
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == "__main__":
    app.run_server(host='0.0.0.0', debug=False, port=8050)
