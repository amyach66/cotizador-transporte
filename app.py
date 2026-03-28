import os
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# 🔑 PON AQUÍ TU API KEY DE GOOGLE (puedes dejarlo vacío por ahora)
API_KEY = os.environ.get("API_KEY")
# 📊 Tarifas base
base_rates = {
    "Business": {"base": 15, "min": 40},
    "Van": {"base": 25, "min": 60}
}

# 🛣️ Tramos por tipo
tiers = {
    "Business": [
        (0,5,2.0),
        (5,10,1.8),
        (10,20,1.5),
        (20,999,1.2)
    ],
    "Van": [
        (0,5,2.5),
        (5,10,2.2),
        (10,20,1.9),
        (20,999,1.6)
    ]
}

# 🧮 Calcular precio
def calcular_precio(tipo, distancia):
    total = 0
    for desde, hasta, precio in tiers[tipo]:
        if distancia > desde:
            millas = min(distancia, hasta) - desde
            total += millas * precio

    total += base_rates[tipo]["base"]
    total = max(total, base_rates[tipo]["min"])
    return round(total, 2)

# 🌍 Obtener distancia desde Google Maps
def obtener_distancia(origen, destino):
    if not API_KEY:
        return 10  # fallback si no hay API

    try:
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origen}&destinations={destino}&units=imperial&key={API_KEY}"
        response = requests.get(url).json()

        metros = response['rows'][0]['elements'][0]['distance']['value']
        return metros / 1609.34
    except:
        return 10  # fallback si falla la API

    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origen}&destinations={destino}&units=imperial&key={API_KEY}"
    response = requests.get(url).json()

    metros = response['rows'][0]['elements'][0]['distance']['value']
    millas = metros / 1609.34
    return millas

# 🏠 Ruta principal
@app.route("/", methods=["GET", "POST"])
def index():
    precio = None
    distancia = None

    if request.method == "POST":
        origen = request.form["origen"]
        destino = request.form["destino"]
        tipo = request.form["tipo"]

        distancia = obtener_distancia(origen, destino)
        precio = calcular_precio(tipo, distancia)

    return render_template("index.html", precio=precio, distancia=distancia)

# ▶️ Ejecutar app
if __name__ == "__main__":
    app.run()