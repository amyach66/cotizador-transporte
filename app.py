from flask import Flask, render_template, request

app = Flask(__name__)


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

    if total < 75:
        total = 75

    return total


# =========================
# ⏱️ DURACION
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
            precio += (minutos - 60) * 0.5

    except:
        pass

    return precio


# =========================
# 🔄 REDONDEO
# =========================
def redondeo_comercial(precio):
    return round(precio / 5) * 5


# =========================
# 🏠 RUTA
# =========================
@app.route("/", methods=["GET", "POST"])
def index():

    precio = None
    distancia = None
    duracion = None
    error = None

    # 🔥 persistencia
    origen = ""
    destino = ""
    tipo = "Business"

    if request.method == "POST":

        origen = request.form.get("origen", "")
        destino = request.form.get("destino", "")
        tipo = request.form.get("tipo", "Business")

        km_str = request.form.get("km_real", "").strip()
        duracion = request.form.get("duracion_real", "0 mins")

        if not km_str:
            error = "Route not calculated. Please try again."
        else:
            km = float(km_str)

            if tipo == "Business":
                precio = calcular_precio_business(km)
            else:
                precio = calcular_precio_van(km)

            precio = ajustar_por_duracion(precio, duracion)
            precio = redondeo_comercial(precio)

            distancia = round(km * 0.621371, 1)
            precio = round(precio, 2)

    return render_template(
        "index.html",
        precio=precio,
        distancia=distancia,
        duracion=duracion,
        error=error,
        origen=origen,
        destino=destino,
        tipo=tipo
    )


if __name__ == "__main__":
    app.run(debug=True)