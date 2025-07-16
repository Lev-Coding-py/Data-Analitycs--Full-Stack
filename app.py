import json
import random
import plotly
import pandas as pd
import plotly.express as px
import plotly.io as pio
from flask import Flask, render_template, request
import pyodbc

app = Flask(__name__)

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost,1433;"
    "DATABASE=Encuestas;"
    "UID=sa;"
    "PWD=Perseo6893!"
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    genero = request.form.get('genero')
    edad = request.form.get('edad')
    p1 = request.form.get('p1')
    p2 = request.form.get('p2')
    p3 = request.form.get('p3')
    p4 = request.form.get('p4')

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Respuestas (Genero, Edad, Pregunta1, Pregunta2, Pregunta3, Pregunta4) VALUES (?, ?, ?, ?, ?, ?)",
            (genero, edad, p1, p2, p3, p4)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return "¡Gracias por responder la encuesta!"
    except Exception as e:
        return f"Error: {e}"

@app.route('/simular-1000')
def simular_1000():
    generos = ["Masculino", "Femenino", "Otro"]
    respuestas = ["Satisfecho", "Neutral", "Insatisfecho"]

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        for _ in range(1000):
            genero = random.choice(generos)
            edad = random.randint(20, 70)
            p1 = random.choice(respuestas)
            p2 = random.choice(respuestas)
            p3 = random.choice(respuestas)
            p4 = random.choice(respuestas)

            cursor.execute(
                "INSERT INTO Respuestas (Genero, Edad, Pregunta1, Pregunta2, Pregunta3, Pregunta4) VALUES (?, ?, ?, ?, ?, ?)",
                (genero, edad, p1, p2, p3, p4)
            )

        conn.commit()
        cursor.close()
        conn.close()
        return "✅ Se insertaron 1000 respuestas simuladas."
    except Exception as e:
        return f"Error al insertar: {e}"

@app.route('/resultados')
def resultados():
    try:
        conn = pyodbc.connect(conn_str)
        query = "SELECT Pregunta1, Pregunta2, Pregunta3, Pregunta4 FROM Respuestas"
        df = pd.read_sql(query, conn)
        conn.close()

        preguntas = ['Pregunta1', 'Pregunta2', 'Pregunta3', 'Pregunta4']
        graficos_html = ""

        for col in preguntas:
            conteo = df[col].value_counts().reset_index()
            conteo.columns = ['Respuesta', 'Cantidad']

            fig = px.bar(
                conteo,
                x='Respuesta',
                y='Cantidad',
                title=f'Respuestas a {col}',
                color='Respuesta',
                text='Cantidad',  
                color_discrete_sequence=px.colors.qualitative.Set2
            )

            fig.update_traces(
                textfont_size=20,        
                textposition='outside'  
            )

            fig.update_layout(
                yaxis_title='Cantidad',
                xaxis_title='Respuesta',
                uniformtext_minsize=8,
                uniformtext_mode='hide',
                margin=dict(t=50, b=50, l=50, r=50)
            )

            graficos_html += plotly.io.to_html(fig, full_html=False)

        return render_template('resultados.html', graficos=graficos_html)

    except Exception as e:
        return f"Error al generar gráficos: {e}"



if __name__ == '__main__':
    app.run(debug=True)
