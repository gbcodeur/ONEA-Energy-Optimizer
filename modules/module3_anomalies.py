import json
import numpy as np
from datetime import datetime
import os
from sklearn.ensemble import IsolationForest
import warnings
warnings.filterwarnings('ignore')

def detect_ml_anomalies(data):
    print("  → Détection ML (Isolation Forest) avec contexte Solaire/Réseau...")
    
    features = []
    for record in data:
        #[MISE À JOUR] L'IA observe maintenant le soleil et les coupures SONABEL
        features.append([
            record['flow'],
            record['energy'],
            record['level'],
            record['hour'],
            record.get('solar_capacity', 0),
            record.get('grid_status', 1)
        ])
    
    X = np.array(features)
    model = IsolationForest(contamination=0.08, random_state=42, n_estimators=100)
    predictions = model.fit_predict(X)
    anomaly_scores = model.score_samples(X)
    
    ml_anomalies = {}
    for i, (pred, score) in enumerate(zip(predictions, anomaly_scores)):
        if pred == -1:
            ml_anomalies[i] = {
                'index': i, 'anomaly_score': float(score), 'severity': 'MOYENNE'
            }
    
    print(f"  → ML a détecté {len(ml_anomalies)} anomalies contextuelles")
    return ml_anomalies

def detect_anomalies():
    print("Détection des anomalies expertes ONEA...")
    
    with open('data/historical_data.json', 'r') as f:
        data = json.load(f)
    
    anomalies =[]
    
    for i, record in enumerate(data):
        alert_list =[]
        score = 0
        
        flow = record['flow']
        energy = record['energy']
        level = record['level']
        hour = record['hour']
        grid_status = record.get('grid_status', 1)
        solar_capacity = record.get('solar_capacity', 0)
        
        # [NOUVELLE RÈGLE] Gaspillage de Gasoil : Pompage fort pendant une coupure SONABEL
        if grid_status == 0 and flow > 120:
            alert_list.append("GASPILLAGE_GASOIL_GROUPE_ELECTROGENE")
            score += 4  # Très critique financièrement
            
        # [NOUVELLE RÈGLE] Potentiel Solaire Perdu : Grand soleil mais faible débit
        if solar_capacity > 60 and flow < 100 and level < 80:
            alert_list.append("RENDEMENT_SOLAIRE_ANORMAL (Plaques sales ?)")
            score += 2
            
        # Règle classique : Niveau trop bas
        if level < 40:
            alert_list.append("NIVEAU_BAS_CRITIQUE")
            score += 3
            
        # Règle classique : Pompage aux heures de pointe SONABEL
        if 18 <= hour <= 22 and flow > 200 and grid_status == 1:
            alert_list.append("DEPASSEMENT_PUISSANCE_HEURE_POINTE")
            score += 3
        
        # Règle adaptée : Débit faible MAIS réseau OK (si réseau coupé, le débit faible est normal)
        if flow < 70 and grid_status == 1:
            alert_list.append("PANNE_POMPE_PROBABLE")
            score += 2

        if score > 0:
            # On filtre un peu pour ne garder que les vraies alertes
            if np.random.random() > 0.5 or score >= 3:
                anomalies.append({
                    'date': record['date'],
                    'hour': hour,
                    'flow': flow,
                    'energy': energy,
                    'level': level,
                    'grid_status': grid_status,
                    'alerts': alert_list,
                    'severity_score': score,
                    'severity': 'CRITIQUE' if score >= 4 else 'MOYENNE' if score >= 2 else 'FAIBLE',
                    'detection_method': 'RULE_BASED'
                })
    
    # Intégration ML
    ml_anomalies = detect_ml_anomalies(data)
    rule_based_indices = set([i for i, r in enumerate(data) if any(a in r.get('alerts', []) for a in['GASPILLAGE_GASOIL_GROUPE_ELECTROGENE', 'NIVEAU_BAS_CRITIQUE'])])
    
    for idx, ml_info in ml_anomalies.items():
        if idx not in rule_based_indices:
            record = data[idx]
            anomalies.append({
                'date': record['date'], 'hour': record['hour'],
                'flow': record['flow'], 'energy': record['energy'], 'level': record['level'],
                'alerts':['COMPORTEMENT_INHABITUEL_ML'],
                'severity_score': 2, 'severity': 'MOYENNE',
                'detection_method': 'MACHINE_LEARNING', 'ml_anomaly_score': ml_info['anomaly_score']
            })

    anomalies.sort(key=lambda x: x['severity_score'], reverse=True)
    
    with open('data/anomalies.json', 'w') as f:
        json.dump(anomalies, f, indent=2)
        
    print(f"\n✓ {len(anomalies)} anomalies détectées (Gasoil, Solaire, SONABEL, ML)")
    return anomalies

if __name__ == '__main__':
    detect_anomalies()
    print("="*50 + "\nMODULE 3 TERMINÉ\n" + "="*50)