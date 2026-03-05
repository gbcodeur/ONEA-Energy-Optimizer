import numpy as np
import pandas as pd
import json
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
import os

# Créer les dossiers si ils n'existent pas
os.makedirs('data', exist_ok=True)
os.makedirs('models', exist_ok=True)

def generate_data():
    """
    Générer 30 jours de données pour une station de pompage
    [MISE À JOUR V2] : Intégration Solaire et Coupures Réseau SONABEL
    """
    print("Génération des données historiques (Météo, Solaire, Réseau)...")
    
    data =[]
    start_date = datetime.now() - timedelta(days=30)
    
    for day in range(30):
        current_date = start_date + timedelta(days=day)
        month = current_date.month
        
        # Température de base
        if month in [3, 4, 5]: temp_day_base = np.random.normal(38, 3) # Saison chaude
        elif month in[6, 7, 8, 9]: temp_day_base = np.random.normal(30, 2) # Pluies
        else: temp_day_base = np.random.normal(33, 2)
        
        for hour in range(24):
            # Température et Humidité
            if 0 <= hour <= 6: temp_ext = temp_day_base - np.random.uniform(8, 12)
            elif 7 <= hour <= 11: temp_ext = temp_day_base - np.random.uniform(2, 5)
            elif 12 <= hour <= 16: temp_ext = temp_day_base + np.random.uniform(0, 3)
            else: temp_ext = temp_day_base - np.random.uniform(3, 7)
            
            temp_ext = max(20, min(45, temp_ext))
            humidity = np.random.uniform(60, 85) if month in [6, 7, 8, 9] else np.random.uniform(15, 40)
            
            # [NOUVEAU] Potentiel Solaire (kWh disponibles)
            # Dépendant de l'heure et de la couverture nuageuse (estimée par humidité)
            solar_capacity = 0
            if 7 <= hour <= 17:
                # Pic solaire entre 11h et 14h
                base_solar = 80 if 11 <= hour <= 14 else 40
                # L'humidité/nuages réduit le rendement de 0 à 30%
                cloud_factor = 1 - (humidity / 100 * 0.3)
                solar_capacity = base_solar * cloud_factor + np.random.normal(0, 5)
            solar_capacity = max(0, round(solar_capacity, 2))
            
            # [NOUVEAU] Statut Réseau SONABEL (1 = OK, 0 = Coupure)
            # Les coupures sont plus fréquentes en pointe (18h-22h) ou saison très chaude
            grid_status = 1
            if temp_ext > 40 and np.random.random() > 0.85: grid_status = 0
            elif 18 <= hour <= 22 and np.random.random() > 0.90: grid_status = 0
            elif np.random.random() > 0.95: grid_status = 0 # Coupure aléatoire

            # Débit et Énergie
            base_flow = 150
            heat_factor = (temp_ext - 35) * 3 if temp_ext > 35 else 0
            
            if 6 <= hour <= 8: flow = base_flow + heat_factor + np.random.normal(50, 10)
            elif 18 <= hour <= 21: flow = base_flow + heat_factor + np.random.normal(70, 15)
            else: flow = base_flow + heat_factor + np.random.normal(0, 20)
            
            flow = max(50, flow)
            energy = flow * 0.8 + np.random.normal(0, 10)
            energy = max(20, energy)
            
            # Niveau réservoir
            if hour < 6: level = 60 + np.random.normal(0, 5)
            elif 6 <= hour <= 12: level = 75 + np.random.normal(0, 5)
            elif 12 <= hour <= 18: level = 65 + np.random.normal(0, 5)
            else: level = 55 + np.random.normal(0, 5)
            
            level = max(30, min(95, level))
            
            data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'hour': hour,
                'day_of_week': current_date.weekday(),
                'temp_ext': round(temp_ext, 1),
                'humidity': round(humidity, 1),
                'solar_capacity': solar_capacity,
                'grid_status': grid_status,
                'flow': round(flow, 2),
                'energy': round(energy, 2),
                'level': round(level, 2)
            })
            
    with open('data/historical_data.json', 'w') as f:
        json.dump(data, f, indent=2)
        
    print(f"✓ {len(data)} enregistrements générés avec données Solaires et Réseau")
    return data

def train_model(data):
    print("\nEntraînement du modèle de prévision IA...")
    df = pd.DataFrame(data)
    
    # Features : On inclut les données météo pour prédire l'énergie nécessaire
    X = df[['hour', 'day_of_week', 'temp_ext', 'humidity']]
    y = df['energy']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    print(f"✓ Score du modèle (R2): {model.score(X_test, y_test):.3f}")
    joblib.dump(model, 'models/energy_model.pkl')
    return model

def make_predictions(model, data):
    print("\nGénération des prévisions à 24h...")
    predictions =[]
    tomorrow = datetime.now() + timedelta(days=1)
    
    for hour in range(24):
        # Météo simulée pour demain
        temp_ext = 35 + np.sin(hour/24 * np.pi) * 8 + np.random.normal(0, 2)
        humidity = 40 + np.cos(hour/24 * np.pi) * 20
        
        # Prédiction Solaire
        solar_capacity = 0
        if 7 <= hour <= 17:
            solar_capacity = (80 if 11 <= hour <= 14 else 40) * (1 - (humidity/100 * 0.3))
        
        # Simulation d'une coupure SONABEL probable à 19h (Pic de conso national)
        grid_status = 0 if hour == 19 else 1
        
        features = [[hour, tomorrow.weekday(), temp_ext, humidity]]
        energy_pred = model.predict(features)[0]
        
        # Estimation du débit
        if 6 <= hour <= 9 or 18 <= hour <= 21: flow_pred = 220
        else: flow_pred = 150
        
        predictions.append({
            'date': tomorrow.strftime('%Y-%m-%d'),
            'hour': hour,
            'temp_ext_predicted': round(temp_ext, 1),
            'solar_capacity_predicted': round(solar_capacity, 1),
            'grid_status_predicted': grid_status,
            'energy_predicted': round(energy_pred, 2),
            'flow_estimated': round(flow_pred, 1),
            'heat_alert': 'OUI' if temp_ext > 38 else 'NON'
        })
        
    with open('data/predictions.json', 'w') as f:
        json.dump(predictions, f, indent=2)
        
    print(f"✓ Prévisions enregistrées. Coupure réseau anticipée à 19h.")
    return predictions

if __name__ == '__main__':
    data = generate_data()
    model = train_model(data)
    predictions = make_predictions(model, data)
    print("="*50 + "\nMODULE 1 TERMINÉ\n" + "="*50)