import findspark
findspark.init()

from pyspark.sql.window import Window
from pyspark.sql.functions import monotonically_increasing_id, ntile

import dash
import os, math
import dash_core_components as dcc
import dash_html_components as html
from shutil import copyfile
from dash.dependencies import Input, Output
from pyspark.ml import Pipeline
from pyspark.ml.classification import GBTClassifier
from pyspark.ml.feature import StringIndexer, VectorIndexer
from pyspark.sql import SparkSession

model = None
click = 0

spark = SparkSession.builder.master("local").appName("classify").getOrCreate()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

hero_list = [{"value": 1, "label": "Annie"}, {"value": 2, "label": "Olaf"}, {"value": 3, "label": "Galio"},
             {"value": 4, "label": "TwistedFate"}, {"value": 5, "label": "XinZhao"}, {"value": 6, "label": "Urgot"},
             {"value": 7, "label": "LeBlanc"}, {"value": 8, "label": "Vladimir"},
             {"value": 9, "label": "Fvaluedlesticks"}, {"value": 10, "label": "Kayle"},
             {"value": 11, "label": "MasterYi"}, {"value": 12, "label": "Alistar"}, {"value": 13, "label": "Ryze"},
             {"value": 14, "label": "Sion"}, {"value": 15, "label": "Sivir"}, {"value": 16, "label": "Soraka"},
             {"value": 17, "label": "Teemo"}, {"value": 18, "label": "Tristana"}, {"value": 19, "label": "Warwick"},
             {"value": 20, "label": "Nunu"}, {"value": 21, "label": "MissFortune"}, {"value": 22, "label": "Ashe"},
             {"value": 23, "label": "Tryndamere"}, {"value": 24, "label": "Jax"}, {"value": 25, "label": "Morgana"},
             {"value": 26, "label": "Zilean"}, {"value": 27, "label": "Singed"}, {"value": 28, "label": "Evelynn"},
             {"value": 29, "label": "Twitch"}, {"value": 30, "label": "Karthus"}, {"value": 31, "label": "Cho'Gath"},
             {"value": 32, "label": "Amumu"}, {"value": 33, "label": "Rammus"}, {"value": 34, "label": "Anivia"},
             {"value": 35, "label": "Shaco"}, {"value": 36, "label": "Dr.Mundo"}, {"value": 37, "label": "Sona"},
             {"value": 38, "label": "Kassadin"}, {"value": 39, "label": "Irelia"}, {"value": 40, "label": "Janna"},
             {"value": 41, "label": "Gangplank"}, {"value": 42, "label": "Corki"}, {"value": 43, "label": "Karma"},
             {"value": 44, "label": "Taric"}, {"value": 45, "label": "Veigar"}, {"value": 48, "label": "Trundle"},
             {"value": 50, "label": "Swain"}, {"value": 51, "label": "Caitlyn"}, {"value": 53, "label": "Blitzcrank"},
             {"value": 54, "label": "Malphite"}, {"value": 55, "label": "Katarina"}, {"value": 56, "label": "Nocturne"},
             {"value": 57, "label": "Maokai"}, {"value": 58, "label": "Renekton"}, {"value": 59, "label": "JarvanIV"},
             {"value": 60, "label": "Elise"}, {"value": 61, "label": "Orianna"}, {"value": 62, "label": "Wukong"},
             {"value": 63, "label": "Brand"}, {"value": 64, "label": "LeeSin"}, {"value": 67, "label": "Vayne"},
             {"value": 68, "label": "Rumble"}, {"value": 69, "label": "Cassiopeia"}, {"value": 72, "label": "Skarner"},
             {"value": 74, "label": "Heimerdinger"}, {"value": 75, "label": "Nasus"},
             {"value": 76, "label": "Nvaluealee"}, {"value": 77, "label": "Udyr"}, {"value": 78, "label": "Poppy"},
             {"value": 79, "label": "Gragas"}, {"value": 80, "label": "Pantheon"}, {"value": 81, "label": "Ezreal"},
             {"value": 82, "label": "Mordekaiser"}, {"value": 83, "label": "Yorick"}, {"value": 84, "label": "Akali"},
             {"value": 85, "label": "Kennen"}, {"value": 86, "label": "Garen"}, {"value": 89, "label": "Leona"},
             {"value": 90, "label": "Malzahar"}, {"value": 91, "label": "Talon"}, {"value": 92, "label": "Riven"},
             {"value": 96, "label": "Kog'Maw"}, {"value": 98, "label": "Shen"}, {"value": 99, "label": "Lux"},
             {"value": 101, "label": "Xerath"}, {"value": 102, "label": "Shyvana"}, {"value": 103, "label": "Ahri"},
             {"value": 104, "label": "Graves"}, {"value": 105, "label": "Fizz"}, {"value": 106, "label": "Volibear"},
             {"value": 107, "label": "Rengar"}, {"value": 110, "label": "Varus"}, {"value": 111, "label": "Nautilus"},
             {"value": 112, "label": "Viktor"}, {"value": 113, "label": "Sejuani"}, {"value": 114, "label": "Fiora"},
             {"value": 115, "label": "Ziggs"}, {"value": 117, "label": "Lulu"}, {"value": 119, "label": "Draven"},
             {"value": 120, "label": "Hecarim"}, {"value": 121, "label": "Kha'Zix"}, {"value": 122, "label": "Darius"},
             {"value": 126, "label": "Jayce"}, {"value": 127, "label": "Lissandra"}, {"value": 131, "label": "Diana"},
             {"value": 133, "label": "Quinn"}, {"value": 134, "label": "Syndra"},
             {"value": 136, "label": "AurelionSol"}, {"value": 141, "label": "Kayn"}, {"value": 143, "label": "Zyra"},
             {"value": 150, "label": "Gnar"}, {"value": 154, "label": "Zac"}, {"value": 157, "label": "Yasuo"},
             {"value": 161, "label": "Vel'Koz"}, {"value": 163, "label": "Taliyah"}, {"value": 164, "label": "Camille"},
             {"value": 201, "label": "Braum"}, {"value": 202, "label": "Jhin"}, {"value": 203, "label": "Kindred"},
             {"value": 222, "label": "Jinx"}, {"value": 223, "label": "TahmKench"}, {"value": 236, "label": "Lucian"},
             {"value": 238, "label": "Zed"}, {"value": 240, "label": "Kled"}, {"value": 245, "label": "Ekko"},
             {"value": 254, "label": "Vi"}, {"value": 266, "label": "Aatrox"}, {"value": 267, "label": "Nami"},
             {"value": 268, "label": "Azir"}, {"value": 412, "label": "Thresh"}, {"value": 420, "label": "Illaoi"},
             {"value": 421, "label": "Rek'Sai"}, {"value": 427, "label": "Ivern"}, {"value": 429, "label": "Kalista"},
             {"value": 432, "label": "Bard"}, {"value": 497, "label": "Rakan"}, {"value": 498, "label": "Xayah"},
             {"value": 516, "label": "Ornn"}]
app.layout = html.Div([
    html.H1(children='League of Legend Prediction'),

    html.H2(id = 'output', children='Wait for result', style={'color': 'red'}),

    html.Div(children='''
    Dashboard: A web Prediction framework for League of Legend .
'''),
    html.Div([
        html.Label('Game Timer (min:sec)'),
        dcc.Input(id='min', value='min', type='number'),
        dcc.Input(id='sec', value='sec', type='number'),

        html.Label('Team 1 tower kill'),
        dcc.Input(id='t1tk', type='number'),

        html.Label('Team 2 tower kill'),
        dcc.Input(id='t2tk', type='number'),

        html.Label('Team 1 inhibitor kill'),
        dcc.Input(id='t1ik', type='number'),

        html.Label('Team 2 inhibitor kill'),
        dcc.Input(id='t2ik', type='number'),

        html.Label('First Blood'),
        dcc.Dropdown(id='fb',
                     options=[
                         {'label': 'None', 'value': '0'},
                         {'label': 'Team 1', 'value': '1'},
                         {'label': 'Team 2', 'value': '2'},
                     ],
                     ),
        html.Label('First Tower'),
        dcc.Dropdown(id='ft',
                     options=[
                         {'label': 'None', 'value': '0'},
                         {'label': 'Team 1', 'value': '1'},
                         {'label': 'Team 2', 'value': '2'},
                     ],
                     ),
        html.Label('First Inhibitor'),
        dcc.Dropdown(id='fi',
                     options=[
                         {'label': 'None', 'value': '0'},
                         {'label': 'Team 1', 'value': '1'},
                         {'label': 'Team 2', 'value': '2'},
                     ],
                     ),
        html.Label('First Baron'),
        dcc.Dropdown(id='fd',
                     options=[
                         {'label': 'None', 'value': '0'},
                         {'label': 'Team 1', 'value': '1'},
                         {'label': 'Team 2', 'value': '2'},
                     ],
                     ),
        html.Label('First Dragon'),
        dcc.Dropdown(id='first_dragon',
                     options=[
                         {'label': 'None', 'value': '0'},
                         {'label': 'Team 1', 'value': '1'},
                         {'label': 'Team 2', 'value': '2'},
                     ],
                     ),
        html.Label('First Rift Herald'),
        dcc.Dropdown(id='first_rift_herald',
                     options=[
                         {'label': 'None', 'value': '0'},
                         {'label': 'Team 1', 'value': '1'},
                         {'label': 'Team 2', 'value': '2'},
                     ],
                     ),

        html.Label('Team 1 Champion List'),
        dcc.Dropdown(id='t1',
                     options=hero_list,
                     multi=True
                     ),

        html.Label('Team 2 Champion List'),
        dcc.Dropdown(id='t2',
                     options=hero_list,
                     multi=True
                     ),



    ], style={'columnCount': 2}),
    html.Button('Submit', id='button')
])

count = 0
def click(num):
    global count
    count = num


@app.callback(
    Output(component_id='output', component_property='children'),
    [Input(component_id='t1', component_property='value'),
     Input(component_id='t2', component_property='value'),
     Input(component_id='min', component_property='value'),
     Input(component_id='sec', component_property='value'),
     Input(component_id='fb', component_property='value'),
     Input(component_id='fi', component_property='value'),
     Input(component_id='fd', component_property='value'),
     Input(component_id='ft', component_property='value'),
     Input(component_id='t1tk', component_property='value'),
     Input(component_id='t2tk', component_property='value'),
     Input(component_id='t2ik', component_property='value'),
     Input(component_id='t2ik', component_property='value'),
     Input(component_id='first_dragon', component_property='value'),
     Input(component_id='first_rift_herald', component_property='value'),
     Input('button', 'n_clicks')]
)
def update_output_div(t1, t2, time_min, time_sec, fb, fi, ft, fd, t1tk, t2tk, t1ik, t2ik, first_dragon, first_rift_herald ,n_click):
    str = 'User Input:   Champion "{}, {}"\n'.format(t1, t2) + 'Time "{} : {}"\n'.format(time_min,
                                                                                         time_sec) + 'First Blood: "{}"\n'.format(
        fb) + 'First Inhibitor "{}"\n'.format(fi) + 'First Tower"{}"\n'.format(ft) + 'Dragon "{}"\n'.format(fd)

    if t1 and len(t1) != 5 or t2 and len(t2) != 5:
        return "Please select 5 champions"

    if not t1 or not t2 or not time_min or not time_sec or not fb or not fi or not ft or not fd:
        return "Please complete input"

    if n_click and n_click != count:
        row = get_prediction(t1, t2, time_min, time_sec, fb, fi, ft, fd, t1tk, t2tk, t1ik, t2ik, first_dragon, first_rift_herald)
        click(n_click)

        l = row['probability'].toArray()
        p = math.sqrt(l[0] ** 2 + l[1] ** 2)

        if row['prediction'] == 0:
            return "Team 1 Win   Probability: {}%".format(p)
        else:
            return "Team 2 Win   Probability: {}%".format(p)


# # Make predictions.


def get_prediction(t1, t2, time_min, time_sec, fb, fi, ft, fd, t1tk, t2tk, t1ik, t2ik, first_dragon, first_rift_herald):
    line =[100 * time_min + time_sec, 9, fb,ft,fi,fd,first_dragon,first_rift_herald, t1[0],t1[1],t1[2],t1[3],t1[4], t1tk, t1ik, t2[0],t2[1],t2[2],t2[3],t2[4],t2tk,t2ik]

    test_line = [2]
    for i in range(len(line)):
        new_item = "%s:%s" % (i + 1, line[i])
        test_line.append(new_item)

    print (test_line)
    copyfile('lib_full.txt', 'lib2.txt')

    with open('test.txt', 'w') as f:
        for item in test_line:
            f.write("%s " % item)
        f.write("\n")
        f.close()

    with open('lib2.txt', 'a') as f:
        for item in test_line:
            f.write("%s " % item)
        f.write("\n")
        f.close()

    data = spark.read.format("libsvm").option("numFeatures", "22").load("lib2.txt")
    (trainingData, testData) = split_by_row_index(data)

    labelIndexer = StringIndexer(inputCol="label", outputCol="indexedLabel").fit(data)
    featureIndexer = VectorIndexer(inputCol="features", outputCol="indexedFeatures", maxCategories=32).fit(data)
    gbt = GBTClassifier(labelCol="indexedLabel", featuresCol="indexedFeatures", maxIter=10)
    pipeline = Pipeline(stages=[labelIndexer, featureIndexer, gbt])
    model = pipeline.fit(trainingData)

    predictions = model.transform(testData)
    predictions.show(1000, False)
    result_list = predictions.collect()
    print(result_list[len(result_list) - 1])
    os.remove("lib2.txt")

    return result_list[len(result_list) - 1]




def split_by_row_index(df, num_partitions=2):
    # Let's assume you don't have a row_id column that has the row order
    t = df.withColumn('_row_id', monotonically_increasing_id())
    # Using ntile() because monotonically_increasing_id is discontinuous across partitions
    t = t.withColumn('_partition', ntile(num_partitions).over(Window.orderBy(t._row_id)))
    return [t.filter(t._partition == i+1).drop('_row_id', '_partition') for i in range(num_partitions)]


if __name__ == '__main__':
    app.run_server(debug=True)