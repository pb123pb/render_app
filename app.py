import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
from predictive_model import predict_service_usage  # Asegúrate de que este módulo esté correctamente implementado

import dash_auth
import os

# Obtener nombres de usuario y contraseñas de las variables de entorno
USERNAME = os.environ.get('DASH_USERNAME')
PASSWORD = os.environ.get('DASH_PASSWORD')

VALID_USERNAME_PASSWORD_PAIRS = {
    USERNAME: PASSWORD
}

app = dash.Dash(__name__)
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)



# Opciones para los desplegables
languages_options = [{'label': lang, 'value': lang} for lang in ['English', 'Spanish', 'French', 'German']]
areas_options = [{'label': area, 'value': area} for area in ['North America', 'Europe', 'Asia', 'South America', 'Africa']]
industries_options = [{'label': ind, 'value': ind} for ind in ['Healthcare', 'Technology', 'Finance', 'Education', 'Retail']]

# Diseño de la aplicación
app.layout = html.Div([
    html.Div([
        html.Img(src='/assets/logo.png', style={'height':'40px', 'width':'auto', 'position':'absolute', 'top':0, 'left':5}),
        html.H1("Therapist Demand Predictive App 📈", style={'text-align': 'center', 'color': '#ecf0f1', 'margin-bottom': '5px', 'font-size': '1.8em'})
    ], style={'position': 'relative'}),

    html.Div([
        html.Div(className='form-group', children=[
            html.Label("Language", className='Label'),
            dcc.Dropdown(id='language-input', options=languages_options, value='English', className='Dropdown', style={'font-size': '1em'}),
        ], style={'margin-bottom': '5px'}),

        html.Div(className='form-group', children=[
            html.Label("Area", className='Label'),
            dcc.Dropdown(id='area-input', options=areas_options, value='North America', className='Dropdown', style={'font-size': '1em'}),
        ], style={'margin-bottom': '5px'}),

        html.Div(className='form-group', children=[
            html.Label("Industry", className='Label'),
            dcc.Dropdown(id='industry-input', options=industries_options, value='Technology', className='Dropdown', style={'font-size': '1em'}),
        ], style={'margin-bottom': '5px'}),

        html.Div(className='form-group', children=[
            html.Label("Number of Employees", className='Label'),
            dcc.Input(id='n-input', type='number', value=1000, className='Input', style={'text-align': 'center', 'width': '95%', 'font-size': '1em'}),
        ], style={'margin-bottom': '5px'}),

        html.Div([
            html.Button('Predict', id='predict-button', n_clicks=0, className='Button', style={'font-size': '1em'})
        ], style={'textAlign': 'center', 'padding': '10px'})
    ], style={'padding': '5px', 'maxWidth': '500px', 'margin': 'auto', 'color': '#ecf0f1'}),

    dcc.Loading(
        id="loading-output",
        children=[html.Div(id='prediction-output', style={'textAlign': 'center'})],
        type="default",
        color="#119DFF"
    ),

    html.Div("This app uses a random forest model to predict service usage. The data for 'available slots' and 'patients per therapist' are obtained from company data.", 
             style={'text-align': 'center', 'margin-top': '20px', 'color': '#ecf0f1', 'font-size': '0.8em'})
], style={'textAlign': 'center', 'position': 'relative', 'padding-bottom': '40px'})


# Callback para la predicción
@app.callback(
    Output('prediction-output', 'children'),
    [Input('predict-button', 'n_clicks')],
    [State('language-input', 'value'), 
     State('area-input', 'value'),
     State('industry-input', 'value'),
     State('n-input', 'value')],
    prevent_initial_call=True
)
def update_output(n_clicks, language, area, industry, n):
    if n_clicks == 0:
        return dash.no_update

    predicted_service_usage, estimated_number_of_users, available_slots, slots_needed, patient_per_therapist_mean, therapists_needed = predict_service_usage(
        language, area, industry, n
    )
    
    data = {
        "Metric": ["Predicted Service Usage (%)", "Estimated Number of Users", "Available Slots in " + language, "Slots Needed", "Patients per Therapist", "Additional Therapists Needed"],
        "Value": [f"{predicted_service_usage:.2f}", f"{estimated_number_of_users:.2f}", f"{available_slots}", f"{slots_needed:.2f}", f"{patient_per_therapist_mean:.2f}", f"{therapists_needed:.2f}"]
    }
    df = pd.DataFrame(data)

    return html.Div([
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in df.columns],
            style_cell={
                'textAlign': 'center',
                'backgroundColor': '#808080',
                'color': 'white',
                'font-size': '0.9em'
            },
            style_header={
                'backgroundColor': '#696969',
                'fontWeight': 'bold',
                'color': 'white',
                'font-size': '0.9em'
            }
        )
    ], style={'maxWidth': '500px', 'margin': 'auto'})

if __name__ == '__main__':
    app.run_server(debug=True)



