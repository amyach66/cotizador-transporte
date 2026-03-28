import os
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# 🔑 PON AQUÍ TU API KEY DE GOOGLE (puedes dejarlo vacío por ahora)
API_KEY = os.environ.get("API_KEY")
# 📊 Tarifas base
base_rates = {
    "Business": {"base": 70, "min": 40},
    "Van": {"base": 75, "min": 60}
}

# 🛣️ Tramos por tipo
tiers = {
    "Business": [
        (0,5,0.9),
        (5,100,1.1),
        (100,200,1.1),
        (200,300,1.1),
        (300,5000,1.2)
    ],
    "Van": [
        (0,5,1.2),
        (5,100,1.2),
        (100,200,1.5),
        (200,300,1.75),
        (300,5000,2)
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
        return 10, "15 mins"  # fallback

    try:
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origen}&destinations={destino}&units=imperial&key={API_KEY}"
        response = requests.get(url).json()

        elemento = response['rows'][0]['elements'][0]

        metros = elemento['distance']['value']
        millas = metros / 1609.34

        duracion = elemento['duration']['text']  # 👈 NUEVO

        return millas, duracion

    except:
        return 10, "15 mins"
# 🏠 Ruta principal
@app.route("/", methods=["GET", "POST"])
def index():
    precio = None
    distancia = None

    if request.method == "POST":
        origen = request.form["origen"]
        destino = request.form["destino"]
        tipo = request.form["tipo"]

        distancia, duracion = obtener_distancia(origen, destino)
        precio = calcular_precio(tipo, distancia)

    return render_template("index.html", precio=precio, distancia=distancia, duracion=duracion)

# ▶️ Ejecutar app
if __name__ == "__main__":
    app.run()