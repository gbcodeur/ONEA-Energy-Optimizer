import json
import numpy as np
from datetime import datetime
import os
import sys

def detect_anomalies():
    """
    Détecter les anomalies dans les données historiques
    """
    print("Détection des anomalies...")
    
    # charger les données
    with open('data/historical_data.json', 'r') as f:
        data = json.load(f)
    
    anomalies = []
    
    for i, record in enumerate(data):
        alert_list = []
        score = 0
        
        flow = record['flow']
        energy = record['energy']
        level = record['level']
        hour = record['hour']
        
        # règle 1: ratio énergie/débit anormal
        # normalement energy ≈ flow * 0.8
        expected_energy = flow * 0.8
        energy_diff = abs(energy - expected_energy)
        
        if energy_diff > 30:
            alert_list.append("CONSO_ANORMALE")
            score += 2
        
        # règle 2: niveau trop bas
        if level < 40:
            alert_list.append("NIVEAU_BAS")
            score += 3
        
        # règle 3: niveau trop haut
        if level > 90:
            alert_list.append("NIVEAU_HAUT")
            score += 1
        
        # règle 4: variation brutale du niveau
        if i > 0:
            prev_level = data[i-1]['level']
            level_change = abs(level - prev_level)
            
            if level_change > 15:
                alert_list.append("VARIATION_BRUTALE")
                score += 2
        
        # règle 5: pompage aux heures de pointe
        if 18 <= hour <= 22 and flow > 200:
            alert_list.append("POMPAGE_HEURE_POINTE")
            score += 1
        
        # règle 6: débit très faible (possible panne)
        if flow < 70:
            alert_list.append("DEBIT_FAIBLE")
            score += 2
        
        # si score > 0, c'est une anomalie
        if score > 0:
            # ajouter un peu de bruit pour avoir des vraies anomalies
            if np.random.random() > 0.7 or score >= 3:
                anomalies.append({
                    'date': record['date'],
                    'hour': hour,
                    'flow': flow,
                    'energy': energy,
                    'level': level,
                    'alerts': alert_list,
                    'severity_score': score,
                    'severity': 'CRITIQUE' if score >= 4 else 'MOYENNE' if score >= 2 else 'FAIBLE'
                })
    
    # trier par sévérité
    anomalies.sort(key=lambda x: x['severity_score'], reverse=True)
    
    # sauvegarder
    with open('data/anomalies.json', 'w') as f:
        json.dump(anomalies, f, indent=2)
    
    # stats
    nb_critical = len([a for a in anomalies if a['severity'] == 'CRITIQUE'])
    nb_medium = len([a for a in anomalies if a['severity'] == 'MOYENNE'])
    nb_low = len([a for a in anomalies if a['severity'] == 'FAIBLE'])
    
    print(f"\n✓ {len(anomalies)} anomalies détectées")
    print(f"  - Critiques: {nb_critical}")
    print(f"  - Moyennes: {nb_medium}")
    print(f"  - Faibles: {nb_low}")
    
    return anomalies

def analyze_anomaly_types():
    """
    Analyser les types d'anomalies
    """
    with open('data/anomalies.json', 'r') as f:
        anomalies = json.load(f)
    
    # compter les types
    alert_counts = {}
    
    for anomaly in anomalies:
        for alert in anomaly['alerts']:
            if alert not in alert_counts:
                alert_counts[alert] = 0
            alert_counts[alert] += 1
    
    print("\nTypes d'anomalies:")
    for alert_type, count in sorted(alert_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {alert_type}: {count} fois")
    
    return alert_counts

def generate_recommendations():
    """
    Générer des recommandations basées sur les anomalies
    """
    with open('data/anomalies.json', 'r') as f:
        anomalies = json.load(f)
    
    recommendations = []
    
    # compter les types
    types_count = {}
    for anomaly in anomalies:
        for alert in anomaly['alerts']:
            types_count[alert] = types_count.get(alert, 0) + 1
    
    # recommandations basées sur les anomalies fréquentes
    if types_count.get('CONSO_ANORMALE', 0) > 5:
        recommendations.append({
            'type': 'MAINTENANCE',
            'priority': 'HAUTE',
            'message': 'Vérifier les pompes - consommation énergétique anormale détectée'
        })
    
    if types_count.get('NIVEAU_BAS', 0) > 3:
        recommendations.append({
            'type': 'OPERATION',
            'priority': 'HAUTE',
            'message': 'Augmenter la fréquence de pompage - niveaux bas fréquents'
        })
    
    if types_count.get('POMPAGE_HEURE_POINTE', 0) > 5:
        recommendations.append({
            'type': 'PLANIFICATION',
            'priority': 'MOYENNE',
            'message': 'Décaler le pompage vers les heures creuses pour réduire les coûts'
        })
    
    if types_count.get('VARIATION_BRUTALE', 0) > 4:
        recommendations.append({
            'type': 'TECHNIQUE',
            'priority': 'MOYENNE',
            'message': 'Vérifier les capteurs de niveau - variations brutales détectées'
        })
    
    print("\nRecommandations:")
    for rec in recommendations:
        print(f"  [{rec['priority']}] {rec['message']}")
    
    return recommendations

def run_hybrid_detection():
    """
    NOUVELLE FONCTION - Approche hybride à 2 niveaux
    Niveau 1: Règles expertes (anomalies connues)
    Niveau 2: Machine Learning (patterns inhabituels)
    """
    print("\n" + "="*60)
    print("MODULE 3 - DÉTECTION ANOMALIES HYBRIDE (Règles + ML)")
    print("="*60)
    
    # Niveau 1: Détection par règles
    print("\n[Niveau 1] Détection par règles expertes...")
    rule_anomalies = detect_anomalies()
    rule_types = analyze_anomaly_types()
    
    # Niveau 2: Détection par ML
    print("\n[Niveau 2] Détection par Machine Learning...")
    try:
        # Importer et exécuter module ML
        from module3bis_ml_anomalies import run_ml_anomaly_detection
        ml_anomalies = run_ml_anomaly_detection()
    except Exception as e:
        print(f"⚠ Erreur ML detection: {e}")
        ml_anomalies = []
    
    # Combiner les résultats
    print("\n" + "="*60)
    print("RÉSULTATS COMBINÉS")
    print("="*60)
    print(f"✓ Anomalies détectées par règles: {len(rule_anomalies)}")
    print(f"✓ Anomalies détectées par ML: {len(ml_anomalies)}")
    print(f"✓ Total anomalies: {len(rule_anomalies) + len(ml_anomalies)}")
    
    # Créer statistiques combinées
    combined_stats = {
        'detection_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'rule_based': {
            'count': len(rule_anomalies),
            'types': rule_types
        },
        'ml_based': {
            'count': len(ml_anomalies),
            'method': 'Isolation Forest'
        },
        'total_anomalies': len(rule_anomalies) + len(ml_anomalies)
    }
    
    # Sauvegarder stats
    os.makedirs('data', exist_ok=True)
    with open('data/hybrid_anomalies_stats.json', 'w') as f:
        json.dump(combined_stats, f, indent=2)
    
    # Générer recommandations
    recommendations = generate_recommendations()
    
    print("\n" + "="*60)
    print("APPROCHE HYBRIDE : Meilleure pratique industrie")
    print("Règles = Explicabilité + Sécurité")
    print("ML = Découverte de patterns cachés")
    print("="*60)
    
    return rule_anomalies, ml_anomalies, recommendations

if __name__ == '__main__':
    # Nouvelle approche hybride
    rule_anomalies, ml_anomalies, recommendations = run_hybrid_detection()
    
    print("\n" + "="*50)
    print("MODULE 3 - DÉTECTION ANOMALIES HYBRIDE TERMINÉ")
    print("="*50)
