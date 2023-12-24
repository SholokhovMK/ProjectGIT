from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import pandas as pd

# Устанавливаем внешние стили для приложения
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Загружаем данные из CSV-файла
df = pd.read_csv('main.csv')

# Получаем уникальные типы услуг
service_types = df['Тип услуги'].unique()

# Определяем структуру и стиль приложения
app = Dash(__name__, external_stylesheets=external_stylesheets)

# Изменяем цветовую схему для темы ремонта машин
colors = {
    'background': '#f2f2f2',
    'text': '#2c3e50'
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    # Заголовок приложения
    html.H1('Автосервис Analytics', style={'text-align': 'center', 'color': colors['text']}),

    # Первый блок: Круговая диаграмма и гистограмма с ползунком
    html.Div([
        # Левая часть блока
        html.Div([
            # Заголовок блока
            html.H4('Выберите тип услуги:', style={'color': '#2c3e50'}),
            # Выпадающий список для выбора типа услуги
            dcc.Dropdown(
                id='service-type',
                options=[{'label': service, 'value': service} for service in service_types],
                value='Техническое обслуживание',
                clearable=False,
                style={'width': '80%', 'margin': '0 auto'}
            ),
            # График временного ряда (линейный график) для отображения динамики доходов и расходов
            dcc.Graph(
                id='time-series',
                figure=px.line(df, x='Дата', y='Общая стоимость (руб)', title='Динамика доходов и расходов')
            ),
            # Круговая диаграмма
            dcc.Graph(
                id='expenses-pie-chart',
                figure=px.pie(df, names='Тип работ', title='Структура расходов по категориям')
            ),
        ], className='six columns'),  # Половина ширины строки

        # Правая часть блока
        html.Div([
            # Заголовок блока
            html.H4('Распределение стоимости услуг:', style={'color': '#2c3e50'}),
            # Гистограмма для анализа прибыли и ее распределения
            dcc.Graph(
                id='profit-histogram',
                figure=px.histogram(df, x='Общая стоимость (руб)', title='Анализ прибыли и ее распределения')
            ),
            # Таблица с данными для отображения ключевых финансовых показателей
            dcc.Table(
                id='financial-table',
                columns=[{'name': col, 'id': col} for col in df.columns],
                data=df.to_dict('records'),
                style_table={'maxHeight': '300px', 'overflowY': 'scroll', 'backgroundColor': colors['background']}
            ),
            # Гистограмма с ползунком для распределения стоимости услуг
            dcc.Graph(id='graph-with-slider'),
            # Ползунок для выбора типа услуги
            dcc.Slider(
                id='year-slider',
                min=0,
                max=len(service_types) - 1,
                step=1,
                value=0,
                marks={str(i): str(service_types[i]) for i in range(0, len(service_types))},
            ),
        ], className='six columns'),  # Половина ширины строки

    ], className='row'),

    # Таблица с данными для отображения ключевых финансовых показателей
    dcc.Table(
        id='financial-table',
        columns=[{'name': col, 'id': col} for col in df.columns],
        data=df.to_dict('records'),
        style_table={'maxHeight': '300px', 'overflowY': 'scroll', 'backgroundColor': colors['background']}
    ),

    # Второй блок: График рассеивания с выбором марки автомобиля и типа оси x
    html.Div([
        # Единственная часть блока
        html.Div([
            # Заголовок блока
            html.H4('График рассеивания:', style={'color': '#2c3e50'}),
            # Выпадающий список для выбора марки автомобиля
            dcc.Dropdown(
                id='car-brand',
                options=[{'label': brand, 'value': brand} for brand in df["Марка автомобиля"].unique()],
                value='Toyota',
                clearable=False,
                style={'width': '80%', 'margin': '0 auto'}
            ),
            # Радиокнопки для выбора типа оси x (линейная или логарифмическая)
            dcc.RadioItems(
                id='crossfilter-xaxis-type',
                options=[
                    {'label': 'Линейная', 'value': 'Linear'},
                    {'label': 'Логарифмическая', 'value': 'Log'}
                ],
                value='Linear',
                labelStyle={'display': 'inline-block', 'marginTop': '5px'}
            ),
            # Выпадающий список (Dropdown) для выбора периода анализа
            dcc.Dropdown(
                id='analysis-period',
                options=[
                    {'label': 'Месяц', 'value': 'month'},
                    {'label': 'Квартал', 'value': 'quarter'},
                    {'label': 'Год', 'value': 'year'}
                ],
                value='month',
                style={'width': '50%', 'margin': '20px auto', 'backgroundColor': colors['background']}
            ),
            # Индикаторы (полоски состояния) для отображения текущих значений финансовых показателей
            dcc.Indicators(
                id='financial-indicators',
                style={'width': '80%', 'margin': '0 auto', 'backgroundColor': colors['background']}
            ),
            # График рассеивания
            dcc.Graph(
                id='scatter-plot',
                figure=px.scatter(df, x='Стоимость работы (руб)', y='Стоимость деталей (руб)',
                                  color='Общая стоимость (руб)',
                                  title='Анализ корреляции между прибылью и финансовыми параметрами')
            ),
        ], className='six columns'),  # Половина ширины строки

    ], className='row', style={'margin-top': '50px'}),
])

# Callback-функции для обновления графиков при взаимодействии с пользователем

# Callback-функция для обновления графика с распределением стоимости услуг по маркам автомобилей
@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('year-slider', 'value'))
def update_figure(selected_year):
    filtered_df = df[df['Тип услуги'] == service_types[selected_year]]

    # Создаем гистограмму
    fig = px.histogram(
        filtered_df,
        x="Общая стоимость (руб)",
        color="Марка автомобиля",
        marginal='box',
        nbins=20,
        labels={'Общая стоимость (руб)': 'Общая стоимость (руб)'}
    )

    # Настраиваем внешний вид графика
    fig.update_layout(
        title='Распределение стоимости услуг',
        xaxis_title='Общая стоимость (руб)',
        yaxis_title='Количество',
        transition_duration=500,
        showlegend=False
    )

    return fig

# Callback-функция для обновления круговой диаграммы с распределением общей стоимости по маркам автомобилей
@app.callback(
    Output("piegraph", "figure"),
    Input("service-type", "value"))
def generate_chart(service_type):
    jjj = df[df['Тип услуги'] == service_type]
    fig = px.pie(
        jjj,
        values='Общая стоимость (руб)',
        names='Марка автомобиля',
        hole=.3,
        title=f'Распределение общей стоимости для услуги: {service_type}'
    )
    return fig

# Callback-функция для обновления графика рассеивания с выбором марки автомобиля и типа оси x
@app.callback(
    Output('scatter-plot', 'figure'),
    Input('service-type', 'value'),
    Input('car-brand', 'value'),
    Input('crossfilter-xaxis-type', 'value'))
def update_graph(service_type, car_brand, xaxis_type):
    dff = df[df['Тип услуги'] == service_type]

    # Создаем график рассеивания
    fig = px.scatter(
        dff[dff['Марка автомобиля'] == car_brand],
        x='Стоимость работы (руб)',
        y='Стоимость деталей (руб)',
        color='Тип работ',
        size='Общая стоимость (руб)',
        hover_name='Номер заказа',
        log_x=True if xaxis_type == 'Log' else False,
        log_y=True if xaxis_type == 'Log' else False
    )

    # Настраиваем внешний вид графика
    fig.update_layout(
        title='График рассеивания стоимости услуг',
        xaxis_title='Стоимость работы (руб)',
        yaxis_title='Стоимость деталей (руб)',
        transition_duration=500
    )

    return fig

# Запуск приложения
if __name__ == '__main__':
    app.run_server(debug=True)
