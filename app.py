import os
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY")

# =========================
# 🔢 CALCULO TIERS
# =========================
def calcular_tiers(km, tiers):
    total = 0

    for desde, hasta, precio in tiers:
        if km > desde:
            tramo = max(0, min(km, hasta) - desde)
            total += tramo * precio

    return total


# =========================
# 💰 BUSINESS
# =========================
def calcular_precio_business(km):
    tiers = [
        (0, 5, 0),
        (5, 100, 0.90),
        (100, 300, 1.10),
        (300, 5000, 1.20)
    ]

    total = calcular_tiers(km, tiers)
    total += 70

    # 🔥 FIX mínimo correcto
    if total < 70:
        total = 70

    return total


# =========================
# 🚐 VAN
# =========================
def calcular_precio_van(km):
    tiers = [
        (0, 5, 0),
        (5, 100, 1.20),
        (100, 200, 1.50),
        (200, 300, 1.75),
        (300, 5000, 2.00)
    ]

    total = calcular_tiers(km, tiers)
    total += 75

    # 🔥 FIX mínimo correcto
    if total < 75:
        total = 75

    return total


# =========================
# ⏱️ AJUSTE POR DURACION
# =========================
def ajustar_por_duracion(precio, duracion_texto):
    try:
        minutos = 0
        partes = duracion_texto.split()

        for i, p in enumerate(partes):
            if "hour" in p:
                minutos += int(partes[i - 1]) * 60
            elif "min" in p:
                minutos += int(partes[i - 1])

        if minutos > 60:
            extra = (minutos - 60) * 0.5
            precio += extra

    except Exception as e:
        print("Error parsing duration:", e)

    return precio


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
# 🔄 REDONDEO
# =========================
def redondeo_comercial(precio):
    return round(precio / 5) * 5


# =========================
# 🌍 DISTANCIA
# =========================
def obtener_distancia(origen, destino):

    if not API_KEY:
        print("⚠️ Missing API_KEY")
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

        elemento = data['rows'][0]['elements'][0]

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
            precio = ajustar_por_duracion(precio, duracion)
            precio = redondeo_comercial(precio)

            precio = round(precio, 2)
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