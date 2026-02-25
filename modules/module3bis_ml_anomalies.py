"""
Module 3bis - Détection d'Anomalies par Machine Learning
Utilise Isolation Forest pour détecter des patterns anormaux
Complète les règles du module 3 avec une approche ML
"""

import json
import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime
import os

def train_isolation_forest(historical_data):
    """
    Entraîner le modèle Isolation Forest sur données historiques
    
    Isolation Forest détecte les anomalies en isolant les observations
    Les points anormaux sont plus faciles à isoler que les points normaux
    """
    # Extraire features pour ML
    features = []
    for record in historical_data:
        features.append([
            record['flow'],
            record['energy'],
            record['level'],
            record['hour']
        ])
    
    X = np.array(features)
    
    # Créer et entraîner le modèle
    # contamination=0.1 signifie qu'on s'attend à ~10% d'anomalies
    model = IsolationForest(
        contamination=0.1,
        random_state=42,
        n_estimators=100
    )
    
    model.fit(X)
    
    print("✓ Modèle Isolation Forest entraîné")
    print(f"  - Données d'entraînement: {len(X)} points")
    print(f"  - Features: flow, energy, level, hour")
    
    return model

def detect_ml_anomalies(model, current_data):
    """
    Détecter anomalies avec le modèle ML entraîné
    Retourne liste d'anomalies avec score de confiance
    """
    anomalies = []
    
    for record in current_data:
        # Préparer features
        features = np.array([[
            record['flow'],
            record['energy'],
            record['level'],
            record['hour']
        ]])
        
        # Prédire: -1 = anomalie, 1 = normal
        prediction = model.predict(features)[0]
        
        # Score d'anomalie (plus négatif = plus anormal)
        anomaly_score = model.score_samples(features)[0]
        
        if prediction == -1:
            # C'est une anomalie ML
            # Déterminer le type probable basé sur les features
            anomaly_type = determine_anomaly_type(record)
            
            anomalies.append({
                'date': record['date'],
                'hour': record['hour'],
                'type': 'ML_DETECTED',
                'subtype': anomaly_type,
                'description': f"Pattern anormal détecté par ML: {anomaly_type}",
                'severity': 2,  # Moyenne par défaut
                'anomaly_score': float(anomaly_score),
                'flow': record['flow'],
                'energy': record['energy'],
                'level': record['level'],
                'detection_method': 'Isolation Forest'
            })
    
    return anomalies

def determine_anomaly_type(record):
    """
    Essayer de déterminer le type d'anomalie basé sur les valeurs
    C'est une interprétation post-hoc pour aider les opérateurs
    """
    flow = record['flow']
    energy = record['energy']
    level = record['level']
    
    # Ratio énergie/débit anormal
    if flow > 0:
        ratio = energy / flow
        if ratio > 1.2:
            return "Surconsommation énergétique"
        elif ratio < 0.5:
            return "Sous-consommation énergétique"
    
    # Combinaisons inhabituelles
    if flow > 200 and level < 35:
        return "Fort pompage mais niveau bas (fuite possible)"
    
    if flow < 80 and level > 85:
        return "Faible pompage mais niveau haut (sur-stockage)"
    
    if energy > 150 and flow < 100:
        return "Forte consommation pour faible débit (inefficacité)"
    
    return "Pattern inhabituel détecté"

def generate_historical_data():
    """
    Générer données historiques 'normales' pour entraînement
    En production, on utiliserait les vraies données ONEA
    """
    print("Génération données historiques pour entraînement ML...")
    
    historical = []
    
    # Simuler 30 jours de données normales
    for day in range(30):
        for hour in range(24):
            # Pattern normal de consommation
            if 6 <= hour <= 9:
                base_flow = 220  # Pic matin
            elif 18 <= hour <= 21:
                base_flow = 240  # Pic soir
            else:
                base_flow = 150  # Normal
            
            # Variation aléatoire normale
            flow = base_flow + np.random.normal(0, 15)
            energy = flow * 0.8 + np.random.normal(0, 10)
            level = 60 + np.random.normal(0, 10)
            
            historical.append({
                'date': f'2026-02-{(day % 28) + 1:02d}',
                'hour': hour,
                'flow': round(flow, 1),
                'energy': round(energy, 1),
                'level': round(level, 1)
            })
    
    print(f"✓ {len(historical)} points de données historiques générés")
    return historical

def run_ml_anomaly_detection():
    """
    Fonction principale: entraîner modèle et détecter anomalies
    """
    print("\n" + "="*60)
    print("MODULE 3bis - DÉTECTION ANOMALIES ML (Isolation Forest)")
    print("="*60)
    
    # 1. Générer/charger données historiques
    historical_data = generate_historical_data()
    
    # 2. Entraîner le modèle
    model = train_isolation_forest(historical_data)
    
    # 3. Charger les mêmes données que le modèle heuristique
    try:
        with open('data/historical_data.json', 'r') as f:
            current_data = json.load(f)
    except FileNotFoundError:
        print("⚠ Fichier historical_data.json introuvable")
        return []
        
    
    # 4. Détecter anomalies ML
    ml_anomalies = detect_ml_anomalies(model, current_data)
    
    # 5. Sauvegarder résultats
    os.makedirs('data', exist_ok=True)
    with open('data/ml_anomalies.json', 'w') as f:
        json.dump(ml_anomalies, f, indent=2)
    
    # 6. Afficher résumé
    print(f"\n✓ Détection ML terminée")
    print(f"  - Points analysés: {len(current_data)}")
    print(f"  - Anomalies ML détectées: {len(ml_anomalies)}")
    
    if ml_anomalies:
        print("\nAnomalies ML trouvées:")
        for anom in ml_anomalies[:5]:  # Afficher max 5
            print(f"  - {anom['date']} {anom['hour']}h: {anom['subtype']}")
    
    return ml_anomalies

if __name__ == "__main__":
    run_ml_anomaly_detection()
