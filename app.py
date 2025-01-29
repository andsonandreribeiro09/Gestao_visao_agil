from flask import Flask, render_template, request
import pandas as pd

# Carregar a planilha
def load_data(file_path):
    df = pd.read_excel(file_path)
    # Remover espaços dos nomes das colunas para facilitar o acesso
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

# Inicializar o Flask
app = Flask(__name__)

# Carregar dados ao iniciar
data_file = "projeto_gestão.xlsx"
data = load_data(data_file)

# Função para filtrar os dados com base no nome do projeto e no status
def filter_data(filters):
    filtered = data.copy()
    
    if filters.get('nome_do_projeto'):
        filtered = filtered[filtered['nome_do_projeto'].str.contains(filters['nome_do_projeto'], case=False, na=False)]
    
    if filters.get('status') and filters['status'] != 'todos':
        filtered = filtered[filtered['status'] == filters['status']]
    
    return filtered

@app.route('/', methods=['GET'])
def index():
    # Obter filtros da URL
    nome_projeto_filter = request.args.get('nome_do_projeto', '')
    status_filter = request.args.get('status', 'todos')
    
    # Preparar filtros
    filters = {
        'nome_do_projeto': nome_projeto_filter,
        'status': status_filter
    }
    
    # Filtrar dados
    filtered_data = filter_data(filters)
    
    # Obter os nomes únicos dos projetos e status para os filtros
    nome_projetos = data['nome_do_projeto'].dropna().unique()
    status_opcoes = ['todos'] + data['status'].dropna().unique().tolist()
    
    return render_template(
        'index.html',
        data=filtered_data.to_dict(orient='records'),
        filters=filters,
        nome_projetos=nome_projetos,
        status_opcoes=status_opcoes
    )

# Rodar o servidor
if __name__ == "__main__":
    app.run(debug=True)
