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
server = app.server
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

extended_text = """
A machine learning model was trained to predict the service usage percentage (number of people using the service out of the total potential) from a database. This database stores information from various companies, such as language, geographic area, business area, number of employees, and service usage.

The machine learning model (random forest) has been benchmarked against a base model. It is trained to predict service usage based on other variables (language, geographic area, business area, and number of employees). The random forest model, which combines decision trees to improve predictions and prevent overfitting, has also been optimized using hyperparameter optimization techniques to enhance its performance in predictions.

With this model, we can predict the service usage percentage using specific company information (language, geographic area, business area, and number of employees).

- With the service usage percentage, we can calculate the number of people who will use the service (number of employees * service usage).
- From our databases, we extract the number of available slots for the company's language, which allows us to calculate the slots that will need to be covered (estimated number of users – available slots in the company's language).
- From the company's database, we can also obtain the average number of patients per therapist, which helps calculate the number of therapists needed to cover the required slots (slots needed / patients per therapist).

Therefore, the steps are:

1. Predicted Service Usage (%): prediction of service usage percentage (random forest machine learning model).
2. Estimated Number of Users: number of users who will use the service (Predicted Service Usage * Number of employees).
3. Available Slots: number of slots available in the language of the new company (extraction from ifeel's databases).
4. Slots Needed: number of slots that will need to be covered (Estimated Number of Users – Available Slots).
5. Patients per Therapist: current average of patients per therapist (extraction from ifeel's databases).
6. Additional Therapists Needed: number of therapists we will need (Slots Needed / Patients per Therapist).
"""

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

    html.Div([
        html.Span("This app uses a random forest model to predict service usage. The data for 'available slots' and 'patients per therapist' are obtained from company data. "),
        html.A("Click here", id="open-modal-link", href="#", style={'color': '#007bff', 'cursor': 'pointer'}),
        html.Span(" for more information.")
    ], style={'text-align': 'center', 'margin-top': '20px', 'color': '#ecf0f1', 'font-size': '0.8em'}),

    dbc.Modal(
        [
            dbc.ModalHeader("Detailed Information", style = {'color': 'black'}),
            dbc.ModalBody(dcc.Markdown(extended_text), style={'color': 'black'}),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-modal-btn", className="ml-auto")
            ),
        ],
        id="modal",
        is_open=False,
    ),
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
    
@app.callback(
    Output("modal", "is_open"),
    [Input("open-modal-link", "n_clicks"), Input("close-modal-btn", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
    
if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))


