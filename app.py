from flask import Flask, request, jsonify, render_template_string
from twilio.twiml.messaging_response import MessagingResponse
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Configura tu clave de OpenAI
openai.api_key = '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'

# Configura conexión con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credenciales.json", scope)
client = gspread.authorize(creds)
sheet = client.open("FormularioMatricula").sheet1

# HTML del formulario
formulario_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Formulario de Matrícula Financiera</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="p-4">
    <h2>Formulario de Matrícula Financiera</h2>
    <form method="POST">
        <div class="mb-3"><label>Nombre completo</label><input type="text" class="form-control" name="nombre" required></div>
        <div class="mb-3"><label>¿Ya iniciaste el proceso?</label><select class="form-control" name="inicio"><option>Sí</option><option>No</option></select></div>
        <div class="mb-3"><label>¿Cómo piensas pagar?</label><select class="form-control" name="pago"><option>Pago de contado</option><option>Financiación bancaria</option><option>No tengo recursos</option></select></div>
        <div class="mb-3"><label>¿Entidad bancaria?</label><input type="text" class="form-control" name="entidad"></div>
        <div class="mb-3"><label>¿Deseas conocer más opciones?</label><select class="form-control" name="opciones"><option>Sí</option><option>No</option></select></div>
        <div class="mb-3"><label>¿Deseas asesor?</label><select class="form-control" name="asesor"><option>Sí</option><option>No</option></select></div>
        <button type="submit" class="btn btn-primary">Enviar</button>
    </form>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        datos = request.form.to_dict()
        sheet.append_row([
            datos['nombre'],
            datos['inicio'],
            datos['pago'],
            datos['entidad'],
            datos['opciones'],
            datos['asesor']
        ])
        prompt = f"""Estudiante: {datos['nombre']}
Inicio matrícula: {datos['inicio']}
Forma de pago: {datos['pago']}
Entidad bancaria: {datos['entidad']}
Quiere conocer otras opciones: {datos['opciones']}
Quiere asesor: {datos['asesor']}
Genera un mensaje de seguimiento personalizado."""
        respuesta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return f"<h3>Respuesta personalizada:</h3><p>{respuesta.choices[0].message.content}</p><a href='/'>Volver</a>"

    return render_template_string(formulario_html)

@app.route('/whatsapp', methods=['POST'])
def whatsapp():
    mensaje = request.form.get('Body')
    nombre = "Estudiante"
    respuesta = f"Hola {nombre}, gracias por tu mensaje: '{mensaje}'. ¿Deseas información sobre matrícula financiera o portafolio bancario?"
    r = MessagingResponse()
    r.message(respuesta)
    return str(r)

if __name__ == '__main__':
    app.run(debug=True)
