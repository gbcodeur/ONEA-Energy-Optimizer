import numpy as np
import pandas as pd
import json
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
import os

# créer les dossiers si ils existent pas
os.makedirs('data', exist_ok=True)
os.makedirs('models', exist_ok=True)

def generate_data():
    """
    Générer 30 jours de données pour une station de pompage
    Inclut données météorologiques (température, humidité)
    """
    print("Génération des données historiques avec météo...")
    
    data = []
    start_date = datetime.now() - timedelta(days=30)
    
    for day in range(30):
        current_date = start_date + timedelta(days=day)
        
        # température de base pour la journée (varie selon saison)
        # Burkina Faso: saison chaude (mars-mai) vs saison des pluies (juin-sept)
        month = current_date.month
        if month in [3, 4, 5]:  # saison très chaude
            temp_day_base = np.random.normal(38, 3)
        elif month in [6, 7, 8, 9]:  # saison des pluies (plus frais)
            temp_day_base = np.random.normal(30, 2)
        else:  # saison sèche
            temp_day_base = np.random.normal(33, 2)
        
        for hour in range(24):
            # température extérieure (cycle journalier)
            # plus fraîche la nuit, pic vers 15h-16h
            if 0 <= hour <= 6:
                temp_ext = temp_day_base - np.random.uniform(8, 12)  # nuit fraîche
            elif 7 <= hour <= 11:
                temp_ext = temp_day_base - np.random.uniform(2, 5)  # montée
            elif 12 <= hour <= 16:
                temp_ext = temp_day_base + np.random.uniform(0, 3)  # pic chaleur
            else:
                temp_ext = temp_day_base - np.random.uniform(3, 7)  # descente soirée
            
            temp_ext = max(20, min(45, temp_ext))  # entre 20°C et 45°C
            
            # humidité (inversement corrélée à température)
            if month in [6, 7, 8, 9]:  # saison des pluies
                humidity = np.random.uniform(60, 85)
            else:  # saison sèche
                humidity = np.random.uniform(15, 40)
            
            # ajuster selon heure (plus humide la nuit)
            if 0 <= hour <= 6:
                humidity += np.random.uniform(5, 15)
            humidity = max(10, min(95, humidity))
            
            # débit d'eau en m3/h
            # CORRÉLATION CHALEUR: plus élevé quand temp > 35°C
            base_flow = 150
            
            # facteur météo: chaleur augmente consommation
            if temp_ext > 35:
                heat_factor = (temp_ext - 35) * 3  # +3 m3/h par degré au-dessus de 35°C
            else:
                heat_factor = 0
            
            # pics habituels matin et soir
            if 6 <= hour <= 8:
                flow = base_flow + heat_factor + np.random.normal(50, 10)
            elif 18 <= hour <= 21:
                flow = base_flow + heat_factor + np.random.normal(70, 15)
            else:
                flow = base_flow + heat_factor + np.random.normal(0, 20)
            
            flow = max(50, flow)  # minimum 50 m3/h
            
            # énergie consommée en kWh
            # dépend du débit + un peu de bruit
            energy = flow * 0.8 + np.random.normal(0, 10)
            energy = max(20, energy)
            
            # niveau du réservoir en %
            # varie selon le pompage et la consommation
            if hour < 6:
                level = 60 + np.random.normal(0, 5)
            elif 6 <= hour <= 12:
                level = 75 + np.random.normal(0, 5)
            elif 12 <= hour <= 18:
                level = 65 + np.random.normal(0, 5)
            else:
                level = 55 + np.random.normal(0, 5)
            
            level = max(30, min(95, level))  # entre 30% et 95%
            
            data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'hour': hour,
                'day_of_week': current_date.weekday(),
                'temp_ext': round(temp_ext, 1),
                'humidity': round(humidity, 1),
                'flow': round(flow, 2),
                'energy': round(energy, 2),
                'level': round(level, 2)
            })
    
    # sauvegarder en JSON
    with open('data/historical_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ {len(data)} enregistrements générés")
    print(f"✓ Données météo intégrées (température + humidité)")
    return data

def train_model(data):
    """
    Entraîner un modèle de prévision avec données météorologiques
    """
    print("\nEntraînement du modèle de prévision (avec météo)...")
    
    # convertir en dataframe
    df = pd.DataFrame(data)
    
    # features: heure, jour semaine, température, humidité
    # SMART CITY: intégration données météo pour anticiper pics de chaleur
    X = df[['hour', 'day_of_week', 'temp_ext', 'humidity']]
    # target: énergie
    y = df['energy']
    
    # split train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # modèle random forest avec météo
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # score
    score = model.score(X_test, y_test)
    print(f"✓ Score du modèle (avec météo): {score:.3f}")
    
    # importance des features
    feature_importance = dict(zip(['hour', 'day_of_week', 'temp_ext', 'humidity'], 
                                   model.feature_importances_))
    print(f"✓ Importance température: {feature_importance['temp_ext']:.3f}")
    print(f"✓ Importance humidité: {feature_importance['humidity']:.3f}")
    
    # sauvegarder le modèle
    joblib.dump(model, 'models/energy_model.pkl')
    print("✓ Modèle sauvegardé")
    
    return model

def make_predictions(model, data):
    """
    Faire des prévisions pour les prochaines 24h avec données météo
    """
    print("\nGénération des prévisions pour 24h (avec météo)...")
    
    predictions = []
    tomorrow = datetime.now() + timedelta(days=1)
    
    # estimer météo de demain basée sur tendances récentes
    recent_data = data[-48:]  # 2 derniers jours
    avg_temp = np.mean([d['temp_ext'] for d in recent_data])
    avg_humidity = np.mean([d['humidity'] for d in recent_data])
    
    month = tomorrow.month
    if month in [3, 4, 5]:
        temp_base = np.random.normal(38, 2)
    elif month in [6, 7, 8, 9]:
        temp_base = np.random.normal(30, 2)
    else:
        temp_base = np.random.normal(33, 2)
    
    for hour in range(24):
        if 0 <= hour <= 6:
            temp_ext = temp_base - np.random.uniform(8, 12)
        elif 7 <= hour <= 11:
            temp_ext = temp_base - np.random.uniform(2, 5)
        elif 12 <= hour <= 16:
            temp_ext = temp_base + np.random.uniform(0, 3)
        else:
            temp_ext = temp_base - np.random.uniform(3, 7)
        
        temp_ext = max(20, min(45, temp_ext))
        
        if month in [6, 7, 8, 9]:
            humidity = np.random.uniform(60, 85)
        else:
            humidity = np.random.uniform(15, 40)
        
        if 0 <= hour <= 6:
            humidity += np.random.uniform(5, 15)
        humidity = max(10, min(95, humidity))

        # ✅ Correction du warning: DataFrame avec noms de colonnes
        features = pd.DataFrame([{
            'hour': hour,
            'day_of_week': tomorrow.weekday(),
            'temp_ext': temp_ext,
            'humidity': humidity
        }])

        # prédiction énergie
        energy_pred = model.predict(features)[0]
        
        predictions.append({
            'date': tomorrow.strftime('%Y-%m-%d'),
            'hour': hour,
            'temp_ext_predicted': round(temp_ext, 1),
            'humidity_predicted': round(humidity, 1),
            'energy_predicted': round(energy_pred, 2),
            'heat_alert': 'OUI' if temp_ext > 38 else 'NON'
        })
    
    with open('data/predictions.json', 'w') as f:
        json.dump(predictions, f, indent=2)
    
    total_energy = sum([p['energy_predicted'] for p in predictions])
    heat_hours = len([p for p in predictions if p['heat_alert'] == 'OUI'])
    
    print(f"✓ Énergie prévue pour demain: {total_energy:.2f} kWh")
    print(f"✓ Heures de forte chaleur (>38°C): {heat_hours}h")
    if heat_hours > 0:
        print(f"⚠️  ALERTE CANICULE: Anticiper hausse consommation d'eau")
    
    return predictions
    
    # sauvegarder
    with open('data/predictions.json', 'w') as f:
        json.dump(predictions, f, indent=2)
    
    total_energy = sum([p['energy_predicted'] for p in predictions])
    heat_hours = len([p for p in predictions if p['heat_alert'] == 'OUI'])
    
    print(f"✓ Énergie prévue pour demain: {total_energy:.2f} kWh")
    print(f"✓ Heures de forte chaleur (>38°C): {heat_hours}h")
    if heat_hours > 0:
        print(f"⚠️  ALERTE CANICULE: Anticiper hausse consommation d'eau")
    
    return predictions

if __name__ == '__main__':
    # étape 1: générer les données
    data = generate_data()
    
    # étape 2: entraîner le modèle
    model = train_model(data)
    
    # étape 3: faire les prévisions
    predictions = make_predictions(model, data)
    
    print("\n" + "="*50)
    print("MODULE 1 - PRÉVISION TERMINÉ")
    print("="*50)
