import os
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY")

# =========================
# 💰 BUSINESS
# =========================
def calcular_precio_business(km):
    total = 0

    tiers = [
        (0, 5, 0.90),
        (5, 100, 1.10),
        (100, 300, 1.20),
        (300, 5000, 1.30)
    ]

    for desde, hasta, precio in tiers:
        if km > desde:
            tramo = min(km, hasta) - desde
            total += tramo * precio

    total += 70
    return round(total, 2)


# =========================
# 🚐 VAN
# =========================
def calcular_precio_van(km):
    total = 0

    tiers = [
        (0, 5, 1.10),
        (5, 100, 1.20),
        (100, 200, 1.50),
        (200, 300, 1.75),
        (300, 5000, 2.00)
    ]

    for desde, hasta, precio in tiers:
        if km > desde:
            tramo = min(km, hasta) - desde
            total += tramo * precio

    total += 80
    return round(total, 2)


# =========================
# 🎯 GENERAL
# =========================
def calcular_precio(tipo, km):
    if tipo == "Business":
        return calcular_precio_business(km)
    elif tipo == "Van":
        return calcular_precio_van(km)
    return 0


# =========================
# 🌍 DISTANCIA
# =========================
def obtener_distancia(origen, destino):
    if not API_KEY:
        return 10, 6.2, "15 mins"

    try:
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"

        params = {
            "origins": origen.strip(),
            "destinations": destino.strip(),
            "units": "metric",
            "key": API_KEY
        }

        response = requests.get(url, params=params)
        data = response.json()

        if data.get("status") != "OK":
            return 10, 6.2, "15 mins"

        elemento = data['rows'][0]['elements'][0]

        if elemento.get("status") != "OK":
            return 10, 6.2, "15 mins"

        metros = elemento['distance']['value']

        km = metros / 1000
        millas = km * 0.621371

        duracion = elemento['duration']['text']

        return km, round(millas, 1), duracion

    except Exception as e:
        print("ERROR:", e)
        return 10, 6.2, "15 mins"


# =========================
# 🏠 RUTA
# =========================
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

        if not origen or not destino or not tipo:
            error = "Please complete all fields"
        else:
            km, millas, duracion = obtener_distancia(origen, destino)
            precio = calcular_precio(tipo, km)
            distancia = millas

    return render_template(
        "index.html",
        precio=precio,
        distancia=distancia,
        duracion=duracion,
        error=error
    )


# =========================
# ▶️ RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)