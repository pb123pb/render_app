# data_and_prediction.py

import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from joblib import load
import base64
import os
import json

encoded_token = os.environ.get('ENCODED_TOKEN')
if encoded_token:
    token_data = json.loads(base64.b64decode(encoded_token.encode()).decode())

# Cargar el modelo y los label encoders
best_dt_regressor = load('best_dt_regressor.joblib')
label_encoders = load('label_encoders.joblib')

# Función para obtener datos de Google Sheets
def get_google_sheets_data(token_data):
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    Therapist_Experience_ID = os.environ.get("THERAPIST_EXPERIENCE_ID")
    credentials = Credentials.from_authorized_user_info(token_data, SCOPES)
    service = build("sheets", "v4", credentials = credentials)
    sheets = service.spreadsheets()

    free_slots_language_continent  = pd.DataFrame(sheets.values().get(spreadsheetId = Therapist_Experience_ID, range = "'Free slots by continent and language'!A:BR").execute().get("values"))
    free_slots_therapists  = pd.DataFrame(sheets.values().get(spreadsheetId = Therapist_Experience_ID, range = "Free_slots!A:BR").execute().get("values"))

    free_slots_therapists.columns = free_slots_therapists.iloc[0]
    free_slots_language_continent.columns = free_slots_language_continent.iloc[0]
    free_slots_therapists = free_slots_therapists[1:] 
    free_slots_language_continent = free_slots_language_continent[1:] 

    return free_slots_language_continent, free_slots_therapists

# Función para realizar predicciones
def predict_service_usage(language, area, industry, n):
    free_slots_language_continent, free_slots_therapists = get_google_sheets_data(token_data)
    
    available_slots = free_slots_language_continent.loc[free_slots_language_continent['Continent_therapist'] == area, language].astype(float).iloc[0]
    patient_per_therapist_mean = pd.to_numeric(free_slots_therapists['Total Actives']).mean()

    input_data = pd.DataFrame([[language, area, industry, n]],
                              columns=['language', 'area', 'industry', 'n'])
    
    input_data_encoded = input_data.copy()
    for column in ['language', 'area', 'industry']:
        input_data_encoded[column] = label_encoders[column].transform(input_data[column])

    predicted_service_usage = best_dt_regressor.predict(input_data_encoded)[0]
    estimated_number_of_users = n * predicted_service_usage / 100
    slots_needed = estimated_number_of_users - available_slots

    if slots_needed <= 0: 
        slots_needed = 0
        therapists_needed = 0

    else:

        therapists_needed = slots_needed / patient_per_therapist_mean

    return predicted_service_usage, estimated_number_of_users, available_slots, slots_needed, patient_per_therapist_mean, therapists_needed
