# 後台處理函數
# 匯入套件
import datetime
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
from wordcloud import WordCloud
from io import BytesIO
import jieba.analyse
import base64

# 匯入自定義程式碼
from app import app
from custom_functions import CreateDBEngine, JobInfoCrawler


# 使用者執行職缺爬蟲程式(chained callbacks)
# 1. set_log_file_name: 設定爬蟲log檔案名稱
# 2. update_job_search_output: 執行爬蟲程式並記錄爬蟲log資訊
# 3. push_log_to_front: 將log資訊輸出到前端畫面讓使用者知道爬蟲進度
# 設定爬蟲log檔案名稱
@app.callback(Output('searchLogFileName', 'children'),
              Input('submitButtonSearch', 'n_clicks'),
              State('searchKeyword', 'value'),
              prevent_initial_call=True)
def set_log_file_name(nClicks, searchKeyword):
    if searchKeyword:
        return searchKeyword + '_' + str(int(datetime.datetime.now().timestamp())) + '.txt'
    else:
        return ''


# 執行爬蟲程式並記錄爬蟲log資訊
@app.callback(Output('searchStatus', 'children'),
              Input('searchLogFileName', 'children'),
              State('searchKeyword', 'value'),
              State('searchMaxPage', 'value'),
              prevent_initial_call=True)
def update_job_search_output(logFileName, searchKeyword, searchMaxPage):

    if logFileName:
        # 執行職缺爬蟲程式
        JobInfoCrawler(keyword=searchKeyword, maxPage=searchMaxPage, logFileName='./log/' + logFileName)
        return '您輸入的關鍵字: ' + searchKeyword + ' 已經下載好囉! 可以點選左側的職缺分析頁面來看看結果!'
    else:
        return '請記得要輸入查詢的關鍵字唷!'


# 將log資訊輸出到前端畫面讓使用者知道爬蟲進度
@app.callback(Output('logUpdateText', 'value'),
              Input('searchLogInterval', 'n_intervals'),
              Input('searchLogFileName', 'children'),
              prevent_initial_call=True)
def push_log_to_front(n, logFileName):

    if logFileName:
        with open('./log/' + logFileName, 'r', encoding='utf-8') as f:
            logInfo = f.read().splitlines()
        return '\n'.join([elem for elem in logInfo if 'POST' not in elem])
    else:
        return '請輸入關鍵字來執行爬蟲程式唷!'


# 使用者切換至職缺分析頁面時更新選項
@app.callback(Output('analysisTarget', 'options'),
              Output('analysisTarget', 'value'),
              Output('analysisDropdownPrep', 'children'),
              Input('jobAnalysisPage', 'n_clicks'))
def update_job_analysis_dropdown(n_clicks):

    # 讀取可查詢職缺分析的選項
    engine = CreateDBEngine()
    query = 'select keyword, searchTime, sampleNums from web_hr.search_info order by searchTime desc;'
    searchInfoData = pd.read_sql(query, con=engine)
    engine.dispose()

    # 建立選項
    options = [{'label': searchInfoData['keyword'][i] + ' - ' + searchInfoData['searchTime'][i] +
                         ' - ' + str(searchInfoData['sampleNums'][i]) + '筆職缺',
                'value': searchInfoData['keyword'][i] + ' - ' + searchInfoData['searchTime'][i] +
                         ' - ' + str(searchInfoData['sampleNums'][i]) + '筆職缺'}
               for i in range(len(searchInfoData))]

    # 建立初始值(最近一次的查詢)
    value = searchInfoData['keyword'][0] + ' - ' + searchInfoData['searchTime'][0] + \
            ' - ' + str(searchInfoData['sampleNums'][0]) + '筆職缺'

    return options, value, ''


# 使用者查詢職缺分析資訊對應後台處理
@app.callback(Output('title', 'children'),
              Output('dataDownloadTime', 'children'),
              Output('sampleInfo', 'children'),
              Output('companyIndustryFig', 'figure'),
              Output('categoryFig', 'figure'),
              Output('catAndSalFig', 'figure'),
              Output('locationFig', 'figure'),
              Output('rqYearFig', 'figure'),
              Output('rqEducationFig', 'figure'),
              Output('rqDeptFig', 'figure'),
              Output('specialtyFig', 'figure'),
              Output('cloudTextFig', 'src'),
              Input('submitButtonAnalysis', 'n_clicks'),
              State('analysisTarget', 'value'),
              prevent_initial_call=True)
def update_job_analysis_output(n_clicks, searchItem):

    # 查詢關鍵字
    searchKey = searchItem.split(' - ')[0]
    # 資料時間
    searchTime = searchItem.split(' - ')[1]

    # 查詢資料表
    engine = CreateDBEngine()
    query = "select * from web_hr.search_data where keyword = '" + searchKey + \
            "' and searchTime = '" + searchTime + "';"
    df = pd.read_sql(query, con=engine)
    engine.dispose()

    # 標題資訊
    title = searchKey + ' - 職缺分析結果'

    # 資料時間資訊
    dataDownloadTime = '資料時間： ' + searchTime

    # 樣本資訊
    sampleInfo = [html.P('在進行分析前，已先行對資料進行以下處理：'),
                  html.Ul([
                      html.Li('移除重複的職缺: 由於觀察資料時發現有重複資料 疑似有公司重複貼出職缺 所以此處透過「職缺其他條件」來過濾重複資料'),
                      html.Li('移除非正職的職缺: 非正職的職缺並非本篇文章想要觀察的目標'),
                      html.Li('移除提供年薪資訊的職缺: 由於年薪可能涵蓋到年終，換算出來的月薪會比實際高，造成資料偏頗，所以先移除不做分析'),
                      html.Li('移除非本國職缺: 外派職缺的薪資通常會比本國高，此處我們僅觀察本國的薪資'),
                      html.Li(['整理職缺薪資資訊: 由於薪資會以「月薪35,000至40,000元以上」、「待遇面議」'
                               '等形式表達，為能夠做量化分析，此處需要先將文字格式轉為數值格式。轉換規則為:',
                               html.Ul([
                                   html.Li('若薪資為一個範圍，例如「月薪35,000至50,000元以上」，則取範圍的上下界值做平均，代表該職缺的薪資'),
                                   html.Li('若薪資為某個值以上，例如「月薪50,000元以上」，則直接以該值作為該職缺的薪資'),
                                   html.Li('若薪資為「待遇面議」，則直接將薪資令為0，在計算相關薪資分析資料時會排除「待遇面議」資料')
                               ])
                               ])
                  ]),
                  html.P('經過上述處理，分析資料的樣本數如下：'),
                  html.Ul([
                      html.Li('總資料筆數：{}'.format(len(df))),
                      html.Li('「待遇面議」資料筆數：{}，佔總資料比：{:.2%}'.format(sum(df['salary'] == 0),
                                                                  sum(df['salary'] == 0) / len(df))),
                      html.Li('「有提供薪資資訊」資料筆數：{}，佔總資料比：{:.2%}'.format(sum(df['salary'] > 0),
                                                                     sum(df['salary'] > 0) / len(df)))
                  ])
                  ]

    # 圖片共用設定
    figConfigLayout = {'title_x': 0.5,
                       'showlegend': False,
                       'hovermode': 'x unified',
                       'font_family': 'Noto Sans TC'}

    # 前10名最需要此職缺的產業長條圖
    companyIndustryData = pd.DataFrame({'職缺數': df['jobCompanyIndustry'].value_counts(),
                                        '比率(%)': round(df['jobCompanyIndustry'].value_counts(normalize=True),
                                                       4) * 100})
    companyIndustryData.reset_index(level=0, inplace=True)
    companyIndustryData = companyIndustryData.rename(columns={'index': '產業'})
    companyIndustryFig = px.bar(companyIndustryData.head(10), x='產業', y='職缺數',
                                hover_name='產業', hover_data=['職缺數', '比率(%)'])
    companyIndustryFig.update_layout(title_text=searchKey + ' - 前10名最需要的產業')
    companyIndustryFig.update_layout(figConfigLayout)

    # 前10名職缺所屬的職業類別
    categoryData = pd.DataFrame({'職缺數': df['jobCategory'].str.split(',').explode().value_counts(),
                                 '比率(%)': round(df['jobCategory'].str.split(',').explode().
                                                value_counts(normalize=True), 4) * 100})
    categoryData.reset_index(level=0, inplace=True)
    categoryData = categoryData.rename(columns={'index': '職業類別'})
    categoryFig = px.bar(categoryData.head(10), x='職業類別', y='職缺數',
                         hover_name='職業類別', hover_data=['職缺數', '比率(%)'])
    categoryFig.update_layout(title_text=searchKey + ' - 職缺前10名所屬職業類別')
    categoryFig.update_layout(figConfigLayout)

    # 薪情最好前10名職業類別(排除薪資為待遇面議的樣本)
    catAndSalData = df[df['salary'] > 0][['jobCategory', 'salary']]
    catAndSalData['jobCategory'] = catAndSalData['jobCategory'].str.split(',')
    catAndSalData = catAndSalData.explode('jobCategory')
    catAndSalData = catAndSalData.groupby('jobCategory').agg(meanSalary=('salary', 'mean'),
                                                             samples=('salary', 'size'))
    catAndSalData = catAndSalData[catAndSalData['samples'] >= 5]  # 計算樣本數需大於5筆
    catAndSalData['meanSalary'] = catAndSalData['meanSalary'].astype(int)
    catAndSalData['ratio'] = round(catAndSalData['samples'] / sum(catAndSalData['samples']), 4) * 100
    catAndSalData.reset_index(level=0, inplace=True)
    catAndSalData = catAndSalData.sort_values(['meanSalary'], ascending=False)
    catAndSalData.columns = ['職業類別', '平均薪資(元)', '計算樣本數', '比率(%)']
    catAndSalFig = px.bar(catAndSalData.head(10), x='職業類別', y='平均薪資(元)',
                          hover_name='職業類別', hover_data=['平均薪資(元)', '計算樣本數', '比率(%)'])
    catAndSalFig.update_layout(title_text=searchKey + ' - 薪情最好前10名職業類別')
    catAndSalFig.update_layout(figConfigLayout)

    # 職缺地點前10名
    locationData = pd.DataFrame({'職缺數': df['jobLocation'].str.slice(0, 3).value_counts(),
                                 '比率(%)': round(df['jobLocation'].str.slice(0, 3).
                                                value_counts(normalize=True), 4) * 100})
    locationData.reset_index(level=0, inplace=True)
    locationData = locationData.rename(columns={'index': '職缺地點'})
    locationFig = px.bar(locationData.head(10), x='職缺地點', y='職缺數',
                         hover_name='職缺地點', hover_data=['職缺數', '比率(%)'])
    locationFig.update_layout(title_text=searchKey + ' - 前10名職缺地點')
    locationFig.update_layout(figConfigLayout)

    # 職缺年資要求
    rqYearData = pd.DataFrame({'職缺數': df['jobRqYear'].value_counts(),
                               '比率(%)': round(df['jobRqYear'].value_counts(normalize=True), 4) * 100})
    rqYearData.reset_index(level=0, inplace=True)
    rqYearData = rqYearData.rename(columns={'index': '職缺年資要求'})
    rqYearFig = px.bar(rqYearData.head(10), x='職缺年資要求', y='職缺數',
                       hover_name='職缺年資要求', hover_data=['職缺數', '比率(%)'])
    rqYearFig.update_layout(title_text=searchKey + ' - 職缺年資要求')
    rqYearFig.update_layout(figConfigLayout)

    # 職缺學歷要求
    rqEducationData = pd.DataFrame({'職缺數': df['jobRqEducation'].value_counts(),
                                    '比率(%)': round(df['jobRqEducation'].value_counts(normalize=True), 4) * 100})
    rqEducationData.reset_index(level=0, inplace=True)
    rqEducationData = rqEducationData.rename(columns={'index': '職缺學歷要求'})
    rqEducationFig = px.bar(rqEducationData.head(10), x='職缺學歷要求', y='職缺數',
                            hover_name='職缺學歷要求', hover_data=['職缺數', '比率(%)'])
    rqEducationFig.update_layout(title_text=searchKey + ' - 職缺學歷要求')
    rqEducationFig.update_layout(figConfigLayout)

    # 職缺科系要求
    rqDeptData = df['jobRqDepartment'][df['jobRqDepartment'] != ''].str.split(',').explode()
    rqDeptData = pd.DataFrame({'職缺數': rqDeptData.value_counts(),
                               '比率(%)': round(rqDeptData.value_counts(normalize=True), 4) * 100})
    rqDeptData.reset_index(level=0, inplace=True)
    rqDeptData = rqDeptData.rename(columns={'index': '職缺科系要求'})
    rqDeptFig = px.bar(rqDeptData.head(10), x='職缺科系要求', y='職缺數',
                       hover_name='職缺科系要求', hover_data=['職缺數', '比率(%)'])
    rqDeptFig.update_layout(title_text=searchKey + ' - 前10名職缺科系要求')
    rqDeptFig.update_layout(figConfigLayout)

    # 職缺技能要求
    specialtyData = df['jobSpecialty'][df['jobSpecialty'] != ''].str.split(',').explode()
    specialtyData = pd.DataFrame({'職缺數': specialtyData.value_counts(),
                                  '比率(%)': round(specialtyData.value_counts(normalize=True), 4) * 100})
    specialtyData.reset_index(level=0, inplace=True)
    specialtyData = specialtyData.rename(columns={'index': '職缺技能要求'})
    specialtyFig = px.bar(specialtyData.head(15), x='職缺技能要求', y='職缺數',
                          hover_name='職缺技能要求', hover_data=['職缺數', '比率(%)'])
    specialtyFig.update_layout(title_text=searchKey + ' - 前15名職缺技能要求')
    specialtyFig.update_layout(figConfigLayout)

    # 職缺其他條件文字雲
    # 加入自定義字典
    jieba.load_userdict('./assets/jieba_dict/userdict.txt')
    # 設定停用詞
    jieba.analyse.set_stop_words('./assets/jieba_dict/stopdict.txt')
    # 透過結巴TF-IDF斷詞來觀察重要詞彙
    allKeyText = jieba.analyse.extract_tags('\n'.join(df['jobOthers'].tolist()), topK=100)
    # 繪製文字雲
    font = './assets/fonts/NotoSansTC-Medium.otf'  # 使用Google開發的思源黑體字體
    wordcloud = WordCloud(background_color="white", font_path=font,
                          width=960, height=720).generate('.'.join(allKeyText))
    img = BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    cloudTextFig = 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

    return title, dataDownloadTime, sampleInfo, companyIndustryFig, categoryFig, catAndSalFig, locationFig, \
           rqYearFig, rqEducationFig, rqDeptFig, specialtyFig, cloudTextFig
