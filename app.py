import os
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# 🔑 API KEY (desde Render o entorno local)
API_KEY = os.environ.get("API_KEY")

# 📊 Tarifas base
base_rates = {
    "Business": {"base": 70, "min": 40},
    "Van": {"base": 75, "min": 60}
}

# 🛣️ Tramos por tipo
tiers = {
    "Business": [
        (0, 5, 0.9),
        (5, 100, 1.1),
        (100, 200, 1.1),
        (200, 300, 1.1),
        (300, 5000, 1.2)
    ],
    "Van": [
        (0, 5, 1.2),
        (5, 100, 1.2),
        (100, 200, 1.5),
        (200, 300, 1.75),
        (300, 5000, 2)
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

# 🌍 Obtener distancia y tiempo desde Google Maps
def obtener_distancia(origen, destino):
    if not API_KEY:
        print("⚠️ API KEY no configurada")
        return 10, "15 mins"

    try:
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"

        # 🔒 limpiar inputs
        origen = origen.strip()
        destino = destino.strip()

        if not origen or not destino:
            return 10, "15 mins"

        params = {
            "origins": origen,
            "destinations": destino,
            "units": "imperial",
            "key": API_KEY
        }

        response = requests.get(url, params=params)
        data = response.json()

        print("📡 Google response:", data)

        if data.get("status") != "OK":
            return 10, "15 mins"

        elemento = data['rows'][0]['elements'][0]

        if elemento.get("status") != "OK":
            return 10, "15 mins"

        metros = elemento['distance']['value']
        millas = round(metros / 1609.34, 1)  # 👈 1 decimal

        duracion = elemento['duration']['text']

        return millas, duracion

    except Exception as e:
        print("❌ ERROR:", e)
        return 10, "15 mins"

# 🏠 Ruta principal
@app.route("/", methods=["GET", "POST"])
def index():
    precio = None
    distancia = None
    duracion = None
    error = None

    if request.method == "POST":
        origen = request.form.get("origen")
        destino = request.form.get("destino")
        tipo = request.form.get("tipo")

        print("📥 Datos recibidos:", origen, destino, tipo)

        # 🔒 Validación
        if not origen or not destino or not tipo:
            error = "Please complete all fields"
        else:
            distancia, duracion = obtener_distancia(origen, destino)
            precio = calcular_precio(tipo, distancia)

    return render_template(
        "index.html",
        precio=precio,
        distancia=distancia,
        duracion=duracion,
        error=error
    )

# ▶️ Ejecutar app
if __name__ == "__main__":
    app.run(debug=True)