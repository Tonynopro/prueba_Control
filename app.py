from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from config import DB_CONFIG
import os

app = Flask(__name__)
CORS(app)


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.route("/")
def home():
    return jsonify({
        "mensaje": "API funcionando"
    })


@app.route("/evento", methods=["POST"])
def registrar_evento():

    data = request.json

    tipo = data.get("tipo")

    if tipo not in ["entrada", "salida"]:
        return jsonify({
            "error": "Tipo inválido"
        }), 400

    connection = get_connection()
    cursor = connection.cursor()

    fecha_hora = data.get("fecha_hora")

    query = """
    INSERT INTO eventos (tipo, fecha_hora)
    VALUES (%s, %s)
    """

    cursor.execute(query, (tipo, fecha_hora))


    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "mensaje": "Evento registrado"
    })


@app.route("/aforo", methods=["GET"])
def obtener_aforo():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT tipo, COUNT(*) 
        FROM eventos
        GROUP BY tipo
    """)

    resultados = cursor.fetchall()

    entradas = 0
    salidas = 0

    for tipo, cantidad in resultados:

        if tipo == "entrada":
            entradas = cantidad

        elif tipo == "salida":
            salidas = cantidad

    aforo = entradas - salidas

    cursor.close()
    connection.close()

    return jsonify({
        "aforo_actual": aforo
    })


if __name__ == "__main__":

    PORT = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=PORT
    )