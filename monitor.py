from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import redis
import json

# Inicializar o Flask
app = Flask(__name__)

# Conectar ao Redis na nuvem (ou localmente para testes)
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Carregar dados iniciais da planilha
DATA_FILE = "projeto_gestao.xlsx"
def load_data():
    df = pd.read_excel(DATA_FILE)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    for _, row in df.iterrows():
        redis_client.hset(f"project:{row['nome_do_projeto']}", mapping=row.to_dict())

data = load_data()

# Filtrar projetos
@app.route('/', methods=['GET'])
def index():
    nome_projeto = request.args.get('nome_do_projeto', '')
    status = request.args.get('status', 'todos')
    
    projetos = []
    for key in redis_client.keys("project:*"):
        projeto = redis_client.hgetall(key)
        if (not nome_projeto or nome_projeto.lower() in projeto['nome_do_projeto'].lower()) and \
           (status == 'todos' or projeto['status'] == status):
            projetos.append(projeto)

    nome_projetos = [redis_client.hget(key, 'nome_do_projeto') for key in redis_client.keys("project:*")]
    
    return render_template('index.html', data=projetos, filters={'nome_do_projeto': nome_projeto, 'status': status}, nome_projetos=nome_projetos)

# Adicionar novo projeto
@app.route('/add_project', methods=['POST'])
def add_project():
    projeto = request.form.to_dict()
    redis_client.hset(f"project:{projeto['nome_do_projeto']}", mapping=projeto)
    return redirect(url_for('index'))

# Atualizar projeto existente
@app.route('/update_project', methods=['POST'])
def update_project():
    projeto = request.form.to_dict()
    redis_client.hset(f"project:{projeto['nome_do_projeto']}", mapping=projeto)
    return redirect(url_for('index'))

# Deletar projeto
@app.route('/delete_project', methods=['POST'])
def delete_project():
    nome_projeto = request.form.get('nome_do_projeto')
    redis_client.delete(f"project:{nome_projeto}")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
