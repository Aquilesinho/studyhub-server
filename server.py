from flask import Flask, request, jsonify
import uuid
import json
import os
from datetime import datetime

app = Flask(__name__)

usuarios = {}
servidores = {}
perfis = {}
online = {}

@app.route("/delete_server", methods=["GET", "POST"])

# ================= SALVAR =================

def salvar():
    with open("dados.json", "w", encoding="utf-8") as f:
        json.dump({
            "usuarios": usuarios,
            "servidores": servidores
        }, f, indent=4, ensure_ascii=False)

def carregar():
    global usuarios, servidores
    if os.path.exists("dados.json"):
        with open("dados.json", "r", encoding="utf-8") as f:
            dados = json.load(f)
            usuarios = dados.get("usuarios", {})
            servidores = dados.get("servidores", {})

# ================= LOGIN =================

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    user = data["user"]
    senha = data["senha"]

    usuarios[user] = senha

    perfis[user] = {
        "telefone": "",
        "foto": "",
        "status": "offline"
    }

    return jsonify({"ok": True})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = data["user"]
    senha = data["senha"]

    if user in usuarios and usuarios[user] == senha:
        online[user] = True
        perfis[user]["status"] = "online"
        return jsonify({"ok": True})
    return jsonify({"ok": False})

@app.route("/logout", methods=["POST"])
def logout():
    data = request.json
    user = data["user"]

    online[user] = False
    perfis[user]["status"] = "offline"

    return jsonify({"ok": True})

@app.route("/set_foto", methods=["POST"])
def set_foto():
    data = request.json
    perfis[data["user"]]["foto"] = data["foto"]
    return jsonify({"ok": True})

@app.route("/set_status", methods=["POST"])
def set_status():
    data = request.json
    perfis[data["user"]]["status"] = data["status"]
    return jsonify({"ok": True})

@app.route("/get_profile/<user>")
def get_profile(user):
    return jsonify(perfis.get(user, {}))

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    user = data["user"]
    senha = data["senha"]

    usuarios[user] = senha
    perfis[user] = {"telefone": ""}

    print(f"[REGISTER] {user}")
    return jsonify({"ok": True})

@app.route("/set_phone", methods=["POST"])
def set_phone():
    data = request.json
    perfis[data["user"]]["telefone"] = data["telefone"]
    return jsonify({"ok": True})

@app.route("/get_profile/<user>")
def get_profile(user):
    return jsonify(perfis.get(user, {}))
# ================= SERVIDOR =================

@app.route("/delete_server", methods=["POST"])
def delete_server():
    data = request.json
    sid = data["sid"]
    user = data["user"]

    if sid in servidores and servidores[sid]["dono"] == user:
        del servidores[sid]
        return jsonify({"ok": True})

    return jsonify({"ok": False})
    
@app.route("/create_server", methods=["POST"])
def create_server():
    data = request.json
    sid = str(uuid.uuid4())[:6]

    servidores[sid] = {
        "nome": data["nome"],
        "dono": data["user"],
        "membros": {data["user"]: "Dono"},
        "materias": {},
        "chat": []
    }

    salvar()
    return jsonify({"server_id": sid})

@app.route("/join_server", methods=["POST"])
def join_server():
    data = request.json
    if data["sid"] in servidores:
        servidores[data["sid"]]["membros"][data["user"]] = "Membro"
        salvar()
        return jsonify({"ok": True})
    return jsonify({"ok": False})

@app.route("/get_server/<sid>")
def get_server(sid):
    return jsonify(servidores.get(sid, {}))

# ================= MATÉRIA =================

@app.route("/add_materia", methods=["POST"])
def add_materia():
    data = request.json
    servidores[data["sid"]]["materias"][data["nome"]] = {}
    salvar()
    return jsonify({"ok": True})

@app.route("/add_cap", methods=["POST"])
def add_cap():
    data = request.json
    mat = servidores[data["sid"]]["materias"][data["mat"]]

    if str(data["num"]) not in mat:
        mat[str(data["num"])] = {
            "nome": data["nome"],
            "texto": ""
        }

    salvar()
    return jsonify({"ok": True})

@app.route("/save_text", methods=["POST"])
def save_text():
    data = request.json
    servidores[data["sid"]]["materias"][data["mat"]][data["cap"]]["texto"] = data["texto"]
    salvar()
    return jsonify({"ok": True})

# ================= CHAT =================

@app.route("/send_msg", methods=["POST"])
def send_msg():
    data = request.json

    hora = datetime.now().strftime("%H:%M")

    msg = {
        "user": data["user"],
        "msg": data["msg"],
        "hora": hora
    }

    servidores[data["sid"]]["chat"].append(msg)

    return jsonify({"ok": True})

# ================= START =================

def iniciar_servidor():
    carregar()
    app.run(host="0.0.0.0", port=5000)

@app.route("/get_servers/<user>")
def get_servers(user):
    lista = []

    for sid, s in servidores.items():
        if user in s["membros"]:
            lista.append({
                "id": sid,
                "nome": s["nome"]
            })

    return jsonify(lista)
    
if __name__ == "__main__":
    iniciar_servidor()
