import dash
from dash import dcc, html

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Cronograma do Projeto em Funil"),
    
    # Funil visual
    html.Div([
        html.Div("Planejamento", style={"height": "100px", "width": "300px", "background-color": "lightblue", "text-align": "center"}),
        html.Div("Execução", style={"height": "100px", "width": "250px", "background-color": "lightgreen", "text-align": "center"}),
        html.Div("Controle", style={"height": "100px", "width": "200px", "background-color": "yellow", "text-align": "center"}),
        html.Div("Conclusão", style={"height": "100px", "width": "150px", "background-color": "lightcoral", "text-align": "center"}),
    ], style={"display": "flex", "flex-direction": "column", "align-items": "center", "margin": "20px 0"})
])

if __name__ == '__main__':
    app.run_server(debug=True)

