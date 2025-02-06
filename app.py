from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify
from flask import Flask, request, redirect, url_for, flash
from sqlalchemy import text

app = Flask(__name__)

app.secret_key = 'supersecretkey'  # Necessário para o uso de flash messages

# Conectar ao PostgreSQL usando SQLAlchemy
DATABASE_URL = "postgresql://linna2025_user:ED4J5Ld3ZetXtGESoMrOR3neDk9D3BJe@dpg-cud55bhopnds73aq1csg-a.oregon-postgres.render.com/linna2025"
engine = create_engine(DATABASE_URL)

# Conectar ao banco de dados utilizando SQLAlchemy
def get_db_connection():
    return engine.connect()

# Carregar dados do PostgreSQL usando SQLAlchemy
def load_data():
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM projetos_gestao", conn)
    return df

# Carregar dados ao iniciar
data = load_data()

# Função para filtrar os dados
# Função para filtrar os dados
def filter_data(filters):
    data = load_data()  # Carrega os dados atualizados sempre que a função for chamada
    filtered = data.copy()
    
    if filters.get('nome_projeto'):
        filtered = filtered[filtered['nome_projeto'].str.contains(filters['nome_projeto'], case=False, na=False)]
    if filters.get('status') and filters['status'] != 'todos':
        filtered = filtered[filtered['status'] == filters['status']]
    
    return filtered


def get_project_by_id(project_id):
    # Usando a conexão do SQLAlchemy para executar a consulta
    conn = engine.connect()
    
    # Criando uma consulta executável
    sql = text("SELECT * FROM projetos_gestao WHERE id = :project_id")
    
    # Passando o parâmetro como dicionário
    result = conn.execute(sql, {"project_id": project_id})
    
    # Obtendo o primeiro resultado
    project = result.fetchone()
    conn.close()

    if project:
        project_dict = {
            'id': project[0],
            'categoria': project[1],
            'nome_projeto': project[2],
            'origem_projeto': project[3],
            'etapa_atual': project[4],
            'descricao_desafio': project[5],
            'lider_projeto': project[6],
            'link_doc': project[7],
            'startup_envolvida': project[8],
            'areas_envolvidas': project[9],
            'cronograma': project[10],
            'dificuldades': project[11],
            'proximos_passos': project[12],
            'ponto_focal': project[13],
            'progresso': project[14],
            'representante_startup': project[15],
            'demandas_pendentes': project[16],
            'acesso': project[17],
            'valor_piloto': project[18],
            'resultado_esperado': project[19],
            'supri_necessidade': project[20],
            'status': project[21]
        }
        return project_dict
    return None


# Página inicial (exibir projetos)
@app.route('/', methods=['GET'])
def index():
    nome_projeto = request.args.get('nome_projeto', '')
    status = request.args.get('status', 'todos')

    filters = {'nome_projeto': nome_projeto, 'status': status}
    filtered_data = filter_data(filters)

    # Pegando lista de projetos e status
    nome_projetos = data['nome_projeto'].dropna().unique()
    status_opcoes = ['todos'] + data['status'].dropna().unique().tolist()

    return render_template('formulario.html', data=filtered_data.to_dict(orient='records'),
                           filters=filters, nome_projetos=nome_projetos, status_opcoes=status_opcoes)


@app.route('/add_project', methods=['POST'])
def add_project():
    projeto = request.form.to_dict()  # Obtém os dados do formulário
    
    required_fields = [
        'categoria', 'nome_projeto', 'origem_projeto', 'etapa_atual', 'descricao_desafio',
        'lider_projeto', 'link_doc', 'startup_envolvida', 'areas_envolvidas', 'cronograma',
        'dificuldades', 'proximos_passos', 'ponto_focal', 'progresso', 'representante_startup',
        'demandas_pendentes', 'acesso', 'valor_piloto', 'resultado_esperado', 'supri_necessidade', 'status'
    ]

    for field in required_fields:
        if not projeto.get(field):
            flash(f'O campo {field} é obrigatório!', 'error')
            return redirect(url_for('index'))

    try:
        projeto['progresso'] = int(projeto['progresso']) if projeto['progresso'].isdigit() else None
        projeto['valor_piloto'] = float(projeto['valor_piloto']) if projeto['valor_piloto'].replace('.', '', 1).isdigit() else None

        with engine.connect() as conn:
            sql = text("""
                INSERT INTO projetos_gestao (
                    categoria, nome_projeto, origem_projeto, etapa_atual, descricao_desafio,
                    lider_projeto, link_doc, startup_envolvida, areas_envolvidas, cronograma,
                    dificuldades, proximos_passos, ponto_focal, progresso, representante_startup,
                    demandas_pendentes, acesso, valor_piloto, resultado_esperado, supriu_necessidade, status
                ) VALUES (
                    :categoria, :nome_projeto, :origem_projeto, :etapa_atual, :descricao_desafio,
                    :lider_projeto, :link_doc, :startup_envolvida, :areas_envolvidas, :cronograma,
                    :dificuldades, :proximos_passos, :ponto_focal, :progresso, :representante_startup,
                    :demandas_pendentes, :acesso, :valor_piloto, :resultado_esperado, :supri_necessidade, :status
                )
            """)
            conn.execute(sql, projeto)
            conn.commit()

        flash('Projeto adicionado com sucesso!', 'success')

    except SQLAlchemyError as e:
        flash(f'Erro ao adicionar projeto: {str(e)}', 'error')

    return redirect(url_for('index'))



# Editar projeto
@app.route('/edit_project/<int:id>', methods=['GET'])
def edit_project(id):
    project = get_project_by_id(id)
    if not project:
        return redirect(url_for('index'))
    return render_template('edit_project.html', project=project)

@app.route('/update_project', methods=['POST'])
def update_project():
    project_id = request.form['id']
    categoria = request.form['categoria']
    nome_projeto = request.form['nome_projeto']
    origem_projeto = request.form['origem_projeto']
    etapa_atual = request.form['etapa_atual']
    descricao_desafio = request.form['descricao_desafio']
    lider_projeto = request.form['lider_projeto']
    link_doc = request.form['link_doc']
    startup_envolvida = request.form['startup_envolvida']
    areas_envolvidas = request.form['areas_envolvidas']
    cronograma = request.form['cronograma']
    dificuldades = request.form['dificuldades']
    proximos_passos = request.form['proximos_passos']
    ponto_focal = request.form['ponto_focal']
    progresso = request.form['progresso']
    representante_startup = request.form['representante_startup']
    demandas_pendentes = request.form['demandas_pendentes']
    acesso = request.form['acesso']
    valor_piloto = request.form['valor_piloto']
    resultado_esperado = request.form['resultado_esperado']
    supriu_necessidade = request.form['supri_necessidade']
    status = request.form['status']

    # Atualiza o projeto no banco de dados utilizando SQLAlchemy
    conn = get_db_connection()
    
    # Atualizar a tabela com os dados do projeto
    sql = text("""
        UPDATE projetos_gestao SET 
            categoria = :categoria, nome_projeto = :nome_projeto, origem_projeto = :origem_projeto, 
            etapa_atual = :etapa_atual, descricao_desafio = :descricao_desafio, lider_projeto = :lider_projeto,
            link_doc = :link_doc, startup_envolvida = :startup_envolvida, areas_envolvidas = :areas_envolvidas, 
            cronograma = :cronograma, dificuldades = :dificuldades, proximos_passos = :proximos_passos,
            ponto_focal = :ponto_focal, progresso = :progresso, representante_startup = :representante_startup,
            demandas_pendentes = :demandas_pendentes, acesso = :acesso, valor_piloto = :valor_piloto,
            resultado_esperado = :resultado_esperado, supriu_necessidade = :supri_necessidade,
            status = :status WHERE id = :id
    """)
    
    # Executar a consulta de atualização com parâmetros
    conn.execute(sql, {
        "categoria": categoria,
        "nome_projeto": nome_projeto,
        "origem_projeto": origem_projeto,
        "etapa_atual": etapa_atual,
        "descricao_desafio": descricao_desafio,
        "lider_projeto": lider_projeto,
        "link_doc": link_doc,
        "startup_envolvida": startup_envolvida,
        "areas_envolvidas": areas_envolvidas,
        "cronograma": cronograma,
        "dificuldades": dificuldades,
        "proximos_passos": proximos_passos,
        "ponto_focal": ponto_focal,
        "progresso": progresso,
        "representante_startup": representante_startup,
        "demandas_pendentes": demandas_pendentes,
        "acesso": acesso,
        "valor_piloto": valor_piloto,
        "resultado_esperado": resultado_esperado,
        "supri_necessidade": supriu_necessidade,
        "status": status,
        "id": project_id
    })
    
    # Confirmar e fechar a conexão
    conn.commit()
    conn.close()

    return redirect(url_for('index'))


@app.route('/delete_project', methods=['POST'])
def delete_project():
    project_id = request.form['id']  # Obtém o ID do projeto do formulário

    try:
        # Conectar ao banco de dados
        conn = get_db_connection()

        # Executar a consulta de deleção
        sql = text("DELETE FROM projetos_gestao WHERE id = :id")
        conn.execute(sql, {"id": project_id})

        # Confirmar e fechar a conexão
        conn.commit()
        conn.close()

        flash('Projeto deletado com sucesso!', 'success')

    except SQLAlchemyError as e:
        flash(f'Erro ao deletar projeto: {str(e)}', 'error')

    return redirect(url_for('index'))  # Redireciona para a página inicial



# Criar o app Dash para o Dashboard
app_dash = Dash(__name__, server=app, routes_pathname_prefix="/dashboard/")

app_dash.layout = html.Div([  
    html.H1("Painel de Indicadores da Gestão de Projetos", style={"text-align": "center", "padding": "20px"}),

    dcc.Dropdown(
        id="status_filter",
        options=[],
        value=None,
        placeholder="Filtrar por Status",
        clearable=True,
        style={"width": "50%", "margin": "auto"}
    ),

    # Card contendo todos os gráficos em uma linha
    html.Div(
        className="card",
        children=[
            html.H4("Indicadores de Gestão de Projetos", style={"text-align": "center", "padding": "10px"}),
            
            # Container para os gráficos em uma linha
            html.Div(
                children=[
                    # Gráfico de barras
                    html.Div(
                        children=[dcc.Graph(id="bar_chart_piloto")],
                        style={"width": "33%", "padding": "10px"}
                    ),
                    
                    # Gráfico de pizza
                    html.Div(
                        children=[dcc.Graph(id="pie_chart")],
                        style={"width": "33%", "padding": "10px"}
                    ),

                    # Gráfico de funil
                    html.Div(
                        children=[dcc.Graph(id="progress_funnel")],
                        style={"width": "33%", "padding": "10px"}
                    ),
                ],
                style={"display": "flex", "justify-content": "space-between", "margin-top": "20px"}
            ),
        ],
        style={
            "border": "1px solid #ddd",
            "border-radius": "8px",
            "padding": "20px",
            "margin-top": "20px",
            "width": "80%",  # Largura do card
            "margin-left": "auto",
            "margin-right": "auto"
        }
    ),

    html.Div([  
        html.A("📋 Voltar para Gestão de Projetos", href="/", target="_self", 
               style={"color": "blue", "display": "block", "padding": "10px", "text-align": "center"})
    ], style={"margin-top": "30px"})
])

@app_dash.callback(
    [Output("bar_chart_piloto", "figure"), Output("pie_chart", "figure"), Output("progress_funnel", "figure"), Output("status_filter", "options")],
    [Input("status_filter", "value")]
)
def update_graphs(selected_status):
    data = load_data()

    # Garantir que a coluna "progresso" seja numérica
    data["progresso"] = pd.to_numeric(data["progresso"], errors="coerce")
    
    filtered_df = data if not selected_status else data[data["status"] == selected_status]

    status_options = [{"label": status, "value": status} for status in data["status"].unique()]
    
    # Gráfico de barras com legendas para as startups
    bar_fig = px.bar(filtered_df, 
                     x="startup_envolvida", 
                     y="valor_piloto", 
                     title="Valor do Piloto vs. Startups", 
                     color="startup_envolvida", 
                     text_auto=True)
    
    # Gráfico de pizza
    pie_fig = px.pie(filtered_df, names="status", title="Distribuição dos Projetos por Status")
    
    # Gráfico de funil com cores personalizadas para o progresso
    progress_mapping = {
        "Pausado": filtered_df[filtered_df["progresso"] <= 2].shape[0],
        "Em Andamento": filtered_df[(filtered_df["progresso"] > 2) & (filtered_df["progresso"] < 10)].shape[0],
        "Concluído": filtered_df[filtered_df["progresso"] == 10].shape[0]
    }
    
    progress_df = pd.DataFrame({
        "Status": list(progress_mapping.keys()),
        "Quantidade": list(progress_mapping.values())
    })
    
    # Cores personalizadas para cada status no funil
    color_map = {"Pausado": "red", "Em Andamento": "orange", "Concluído": "green"}
    progress_funnel = px.funnel(progress_df, x="Quantidade", y="Status", title="Progresso dos Projetos", color="Status", 
                                color_discrete_map=color_map)
    
    return bar_fig, pie_fig, progress_funnel, status_options

    


# Rota para mostrar o formulário
@app.route('/criar_equipe', methods=['GET'])
def mostrar_formulario():
    return render_template('criar_equipe.html')

# Rota para criar uma equipe
@app.route('/criar_equipe', methods=['POST'])
def criar_equipe():
    try:
        nome = request.form['nome']
        visibilidade = request.form['visibilidade'] == 'true'
        membros = request.form['membros'].split(',')
        aprovacao_necessaria = request.form['aprovacao_necessaria'] == 'true'
        papel = request.form['papel']  # Captura o papel escolhido para cada membro

        # Validação dos dados
        if not nome or not visibilidade:
            return jsonify({"erro": "Nome e visibilidade são obrigatórios"}), 400

        with engine.connect() as conn:
            with conn.begin():  # Transação segura
                # Inserir equipe na tabela "equipes"
                sql = text("""
                    INSERT INTO equipes (nome, visibilidade, aprovacao_necessaria) 
                    VALUES (:nome, :visibilidade, :aprovacao_necessaria)
                    RETURNING id
                """)
                result = conn.execute(sql, {
                    "nome": nome,
                    "visibilidade": visibilidade,
                    "aprovacao_necessaria": aprovacao_necessaria
                })
                equipe_id = result.fetchone()[0]

                # Inserir membros na tabela "equipe_membros"
                for membro in membros:
                    sql_membro = text("""
                        INSERT INTO equipe_membros (equipe_id, membro, papel) 
                        VALUES (:equipe_id, :membro, :papel)
                    """)
                    conn.execute(sql_membro, {"equipe_id": equipe_id, "membro": membro.strip(), "papel": papel})

        return jsonify({"mensagem": "Equipe criada com sucesso", "equipe_id": equipe_id}), 201

    except SQLAlchemyError as e:
        return jsonify({"erro": "Erro no banco de dados", "detalhes": str(e)}), 500
    except Exception as e:
        return jsonify({"erro": "Erro inesperado", "detalhes": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=False)
