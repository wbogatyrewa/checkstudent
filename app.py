import dash
import dash_html_components as html
import pandas as pd
import base64
from datetime import datetime as dt
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import random
import re
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

""" Запуск приложения """
server = Flask(__name__)
app = dash.Dash(__name__, suppress_callback_exceptions=True)

""" Подключение к базе данных """
con = server.config[
    'SQLALCHEMY_DATABASE_URI'] = 'mysql://c19441_checkoutheadergang_na4u_r:RiZyiVodxivon88@localhost/c19441_checkoutheadergang_na4u_r?charset=utf8'
db = SQLAlchemy(server)


""" Выводится страница сайта """
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

""" Собираем данные, которые отправляются в базу """
sent_data = {
    "id_stud": '',
    "name": '',
    "groups": '',
    "photo": ''
}


def encode_image(image_file):
    """ Энкодим фотографии, чтобы выводить их в веб-приложение.
        Функция возвращает энкод фото"""
    encoded = base64.b64encode(open(image_file, 'rb').read())
    return 'data:image/png;base64,{}'.format(encoded.decode())


def students(con):
    """ Получаем таблицу Students из базы данных.
        Преобразуем ее к DataFrame.
        Функция возвращает DataFrame таблицы """
    Students = pd.read_sql('SELECT * FROM Students', con)
    dict_students = Students.to_dict('records')
    pd.DataFrame(dict_students)
    return dict_students


def log(con):
    """ Получаем таблицу Log из базы данных.
        Преобразуем ее к DataFrame
        Функция возвращает DataFrame таблицы"""
    Log = pd.read_sql('SELECT * FROM Log', con)
    dict_log = Log.to_dict('records')
    pd.DataFrame(dict_log)
    return dict_log


def timeLessons():
    """ Время занятий """
    return ['8:00 - 9:35', '9:45 - 11:20',
            '11:30 - 13:05', '13:35 - 15:10',
            '15:20 - 16:55', '17:05 - 18:40']


def checkStudent(photo):
    """ Возвращается статус студента на занятии.
        Если в базе нет фотографии (т.е. длина фото == 0) студента на занятии, то возвращяем 'Отсутствовал'.
        Если есть фотография студента на занятии( т.е. длина фото != 0), то возвращаем 'Присутствовал' """
    if len(photo) == 0:
        return 'Отсутствовал'
    else:
        return 'Присутствовал'


def create_id():
    """ Рандомно генерируем id нового студента.
        Нужно сделать неповторяющее id.
        А еще нужно обновлять id при каждом заходе в 'Паспорт студента' """
    id = random.randint(1000000, 99999999)
    return id


""" Главная страница сайта, выводит результаты учета посещаемости в таблицу, 
    в которой отражается статус студента – его присутствие или отсутствие.
    На главной странице сайта есть возможность выбрать дату и время лекции или семинара. """
main_page_layout = html.Div([
    html.H1('Учет посещаемости', style={'textAlign': 'center', 'color': '#373a3c'}),
    html.H3('Комната: 103/3г', style={'color': '#373a3c'}),
    html.Div([
        # Календарь с возможностью выбора даты занятия
        dcc.DatePickerSingle(
        id='my-date-picker-single',
        min_date_allowed=dt(2020, 1, 1),
        max_date_allowed=dt(2020, 12, 31),
        initial_visible_month=dt(2020, 5, 22),
        placeholder='Выберите дату занятия',
        date=dt(2020, 5, 22)
        ),
        html.Div(id='output-container-date-picker-single'),
        html.Br(),
        # Выпадающий список, в котором можно выбрать время занятия
        dcc.Dropdown(style={'width': '200px'},
                    options=[{'label': j, 'value': j} for j in timeLessons()],
                    placeholder='Выберите время занятия'),
    ]),
    html.Br(),
    # Ссылка для перехода к log
    dcc.Link('Лог занятия', href='/log'),
    html.Br(),
    # Вывод результатов учета посещаемости в таблице
    html.Table(style={'table-layout': 'fixed',
                      'width': '100%',
                      'text-align': 'left',
                      'color': '#373a3c',
                      'font-family': 'sans-serif'},
               children=[
                        html.Div([html.Tr([
                                html.Th(style={'width': '400px', 'padding': '20px', 'border-collapse': 'collapse',
                                                   'color': 'white', 'background-color': '#373a3c'},
                                        children=j) for j in ['ФИО', 'Фото', 'Статус']
                                ]),
                            ]),
                        html.Div([html.Tr([
                               html.Td(style={'width': '400px', 'padding': '20px',
                                           'border-bottom': '2px solid #dee2e6', 'border-collapse': 'collapse'},
                                    children=students(con)[i]['name']),
                               html.Td(style={'width': '400px', 'padding': '20px',
                                              'border-bottom': '2px solid #dee2e6', 'border-collapse': 'collapse'},
                                       children=html.Img(src=encode_image('../' + students(con)[i]['photo']), height=100,
                                                         width=125)),
                               html.Td(style={'width': '400px', 'padding': '20px',
                                              'border-bottom': '2px solid #dee2e6', 'border-collapse': 'collapse'},
                                       children=checkStudent(log(con)[i]['photo']))
                           ]) for i in range(len(students(con)))
                       ])
               ])
])



@app.callback(
    Output('output-container-date-picker-single', 'children'),
    [Input('my-date-picker-single', 'date')])
def update_output(date):
    """ Возвращает дату, выбранную пользователем через календарь """
    if date is not None:
        date = dt.strptime(re.split('T| ', date)[0], '%Y-%m-%d')
        date_string = date.strftime('%B %d, %Y')
        return ' '


def passport(id):
    """ Страница 'Паспорт студента', которая позволяет добавлять данные студента и его эталонную фотографию. """
    # Группы студентов, доступные для выбора
    groups = ['КЭ-101', 'КЭ-102', 'КЭ-103',
              'КЭ-201', 'КЭ-202', 'КЭ-203',
              'КЭ-301', 'КЭ-302', 'КЭ-303',
              'КЭ-401', 'КЭ-402', 'КЭ-403']

    # отправляем id в словарь, который отправляется в базу
    sent_data["id_stud"] = id

    return html.Div(children=[
        html.Div(id="zatemnenie", children=[
            html.A(className='close', href='http://checkoutheadergang.na4u.ru/log'),
            html.Div(id="okno", children=[
                html.H1("Паспорт студента"),
                html.Div(style={'textAlign': 'left'},
                         children=[
                             # Выводим id, которое присваивается конкретному студенту
                             html.P('id: %s' % id),
                             # Поле для ввода фамилии, имени и отчества студента
                             html.Div([html.P('ФИО: '),
                                       html.Div([dcc.Input(id='input_name', type='text', size='65',
                                                           placeholder='Введите ФИО', name='name')]),
                                       html.P(id='output_name')]),
                             # Выпадающий список групп студентов
                             html.Div([
                                 html.P('Группа: '),
                                 dcc.Dropdown(
                                     id='dropdown_group',
                                     options=[{'label': j, 'value': j} for j in groups],
                                     placeholder='Выберете группу',
                                 ),
                                 html.P(id='dropdown_group_out')
                             ]),
                             # Кнопка загрузки эталонной фотографии студента
                             html.P('Фото: '),
                             dcc.Upload(id='upload-image',
                                        children=html.Button('Выбрать фото'),
                                        multiple=True),
                             html.Div(id='output-image-upload')
                         ]),
                # По кнопке 'Сохранить' отправляем введенные данные в базу
                html.Button(id="save-button", children="Сохранить", type='submit'),
                html.Div(id='press-save-state'),
            ])
        ]),
        # Кнопка перехода на страницу 'Паспорт студента'
        html.A(href='#zatemnenie', className='open', children='Добавить студента')
    ])

""" В Логе занятия находятся данные о студенте: его id, имя, группа, время фото и фото, полученное на занятии. """
log_page_layout = html.Div([
    html.H1('Лог занятия', style={'textAlign': 'center', 'color': '#373a3c'}),
    # Выводим дату и время занятия
    html.H2(style={'textAlign': 'center', 'color': '#373a3c'},
            children=log(con)[0]['time'][:11]),
    # Вызов функции со страницей 'Паспорт студента'
    html.Div(passport(create_id())),
    # Таблица с данными студентов на занятии (если студент отсутствовал, но не может находиться в этой таблице)
    html.Table(style={'table-layout': 'fixed',
                      'width': '100%',
                      'text-align': 'left',
                      'color': '#373a3c',
                      'font-family': 'sans-serif'},
               children=[
                   html.Div(style={},
                            children=[
                                html.Tr([
                                    html.Th(style={'width': '300px', 'padding': '20px', 'border-collapse': 'collapse',
                                                   'color': 'white', 'background-color': '#373a3c'},
                                            children=j) for j in ['Время кадра', 'Фото', 'id', 'ФИО', 'Группа']
                                ]),
                            ]),
                   html.Div([
                       html.Tr([
                           html.Td(style={'width': '300px', 'padding': '20px',
                                          'border-bottom': '2px solid #dee2e6', 'border-collapse': 'collapse', },
                                   children=log(con)[i]['time'][11:]),
                           html.Td(style={'width': '300px', 'padding': '20px',
                                          'border-bottom': '2px solid #dee2e6', 'border-collapse': 'collapse'},
                                   children=
                                   html.Img(src=encode_image('../' + log(con)[i]['photo']), height=100, width=125)
                                   ),
                           html.Td(style={'width': '300px', 'padding': '20px',
                                          'border-bottom': '2px solid #dee2e6', 'border-collapse': 'collapse'},
                                   children=log(con)[i]['id_stud']),
                           html.Td(style={'width': '300px', 'padding': '20px',
                                          'border-bottom': '2px solid #dee2e6', 'border-collapse': 'collapse'},
                                   children=students(con)[i]['name']),
                           html.Td(style={'width': '300px', 'padding': '20px',
                                          'border-bottom': '2px solid #dee2e6', 'border-collapse': 'collapse'},
                                   children=students(con)[i]['groups'])

                       ]) for i in range(len(students(con)))
                   ])
               ])
])


def parse_contents(contents, filename):
    """ Декодим загруженную пользователем фотографию.
        Генерируем путь до фото и сохраняем его в наш словарь, а само фото загружаем на сервер """
    edit_string = contents[23:]
    edit_string.replace("\n", "")
    imgdata = base64.b64decode(edit_string)
    filename = '{}_true_image.jpg'.format(sent_data['id_stud'])
    with open("../app/student/" + filename, 'wb') as f:
        f.write(imgdata)
    # Отправляем путь до фото в базу
    sent_data["photo"] = "app/student/" + filename
    return html.Div([
        html.Img(src=contents, height=100, width=125),
        html.P(filename)
    ])


@app.callback(
    Output('output_name', 'children'),
    [Input('input_name', 'value')]
)
def input_fio(input_name):
    """ Введенные пользователем ФИО сохраняем в наш словарь """

    sent_data["name"] = input_name
    return input_name


@app.callback(
    Output('dropdown_group_out', 'children'),
    [Input('dropdown_group', 'value')]
)
def update_dropdown(group):
    """ Выбранная пользователем группа сохраняется в наш словарь """

    sent_data["groups"] = group
    return group


@app.callback(
    Output('output-image-upload', 'children'),
    [Input('upload-image', 'contents')],
    [State('upload-image', 'filename')]
)
def update_output(list_of_contents, list_of_names):
    """ Загружается пользователем фотография """

    if list_of_contents is not None:
        photo = [parse_contents(c, n) for c, n in zip(list_of_contents, list_of_names)]
        return photo


@app.callback(
    Output('press-save-state', 'children'),
    [Input('save-button', 'n_clicks')]
)
def sent_data_of_student(n_clicks):
    """  Отправляем собранные данные в базу """
    if n_clicks:
        # еще раз подключимся к базе данных
        con = server.config[
        'SQLALCHEMY_DATABASE_URI'] = 'mysql://c19441_checkoutheadergang_na4u_r:RiZyiVodxivon88@localhost/c19441_checkoutheadergang_na4u_r?charset=utf8'
        sentData_to_df = pd.DataFrame([sent_data])
        sentData_to_df.to_sql(name="Students", con=con, if_exists='append', index=False)
        return 'Сохранено'



@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    """ Если ссылка == '/log', то запускаем страницу 'Лог занятия'.
        Если ссылка другая, то запускаем главную страницу приложения """
    if pathname == '/log':
        return log_page_layout
    else:
        return main_page_layout


if __name__ == '__main__':
    app.run_server(debug=True)