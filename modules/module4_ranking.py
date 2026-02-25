import json
import numpy as np
from datetime import datetime, timedelta

def generate_stations_data():
    """
    Générer les données pour plusieurs stations de pompage
    """
    print("Génération des données multi-stations...")
    
    stations = [
        {'id': 'STATION_01', 'name': 'Ouagadougou Centre', 'capacity': 500},
        {'id': 'STATION_02', 'name': 'Ouaga Nord', 'capacity': 400},
        {'id': 'STATION_03', 'name': 'Ouaga Sud', 'capacity': 350},
        {'id': 'STATION_04', 'name': 'Bobo-Dioulasso', 'capacity': 450},
        {'id': 'STATION_05', 'name': 'Koudougou', 'capacity': 300},
        {'id': 'STATION_06', 'name': 'Banfora', 'capacity': 250}
    ]
    
    stations_data = []
    
    for station in stations:
        # générer 7 jours de données pour chaque station
        total_energy = 0
        total_flow = 0
        anomaly_count = 0
        
        for day in range(7):
            for hour in range(24):
                # débit variable selon la station
                base_flow = station['capacity'] * 0.5
                flow = base_flow + np.random.normal(0, 30)
                flow = max(50, min(station['capacity'], flow))
                
                # énergie (avec efficacité variable selon station)
                # certaines stations sont moins efficaces
                efficiency = np.random.uniform(0.7, 1.0)
                energy = flow * 0.8 / efficiency
                
                total_energy += energy
                total_flow += flow
                
                # simuler des anomalies
                if np.random.random() > 0.92:
                    anomaly_count += 1
        
        # calculer les métriques
        avg_energy_per_m3 = total_energy / total_flow
        
        # coût total (mix des tarifs)
        avg_price = 75  # prix moyen
        total_cost = total_energy * avg_price
        
        # score d'efficacité (0-100)
        # meilleur score = moins d'énergie par m3
        efficiency_score = max(0, 100 - (avg_energy_per_m3 - 0.8) * 100)
        
        stations_data.append({
            'id': station['id'],
            'name': station['name'],
            'capacity_m3h': station['capacity'],
            'total_energy_kwh': round(total_energy, 2),
            'total_flow_m3': round(total_flow, 2),
            'total_cost_fcfa': round(total_cost, 2),
            'avg_energy_per_m3': round(avg_energy_per_m3, 3),
            'anomaly_count': anomaly_count,
            'efficiency_score': round(efficiency_score, 1)
        })
    
    return stations_data

def rank_stations(stations_data):
    """
    Classer les stations selon différents critères
    """
    print("\nClassement des stations...")
    
    # 1. Classement par consommation totale
    by_energy = sorted(stations_data, key=lambda x: x['total_energy_kwh'], reverse=True)
    
    # 2. Classement par coût
    by_cost = sorted(stations_data, key=lambda x: x['total_cost_fcfa'], reverse=True)
    
    # 3. Classement par efficacité (meilleur = premier)
    by_efficiency = sorted(stations_data, key=lambda x: x['efficiency_score'], reverse=True)
    
    # 4. Classement par anomalies
    by_anomalies = sorted(stations_data, key=lambda x: x['anomaly_count'], reverse=True)
    
    ranking = {
        'by_energy_consumption': [
            {
                'rank': i+1,
                'station_id': s['id'],
                'station_name': s['name'],
                'total_energy_kwh': s['total_energy_kwh'],
                'category': 'TRES_ENERGIVORE' if i < 2 else 'ENERGIVORE' if i < 4 else 'NORMAL'
            }
            for i, s in enumerate(by_energy)
        ],
        'by_cost': [
            {
                'rank': i+1,
                'station_id': s['id'],
                'station_name': s['name'],
                'total_cost_fcfa': s['total_cost_fcfa']
            }
            for i, s in enumerate(by_cost)
        ],
        'by_efficiency': [
            {
                'rank': i+1,
                'station_id': s['id'],
                'station_name': s['name'],
                'efficiency_score': s['efficiency_score'],
                'category': 'EXCELLENT' if i < 2 else 'BON' if i < 4 else 'A_AMELIORER'
            }
            for i, s in enumerate(by_efficiency)
        ],
        'by_anomalies': [
            {
                'rank': i+1,
                'station_id': s['id'],
                'station_name': s['name'],
                'anomaly_count': s['anomaly_count'],
                'priority': 'URGENTE' if i < 2 else 'MOYENNE' if i < 4 else 'FAIBLE'
            }
            for i, s in enumerate(by_anomalies)
        ],
        'detailed_data': stations_data
    }
    
    return ranking

def generate_action_plan(ranking):
    """
    Générer un plan d'action basé sur le classement
    """
    print("\nGénération du plan d'action...")
    
    action_plan = []
    
    # stations les plus énergivores
    top_energy = ranking['by_energy_consumption'][:2]
    for station in top_energy:
        action_plan.append({
            'station': station['station_name'],
            'type': 'REDUCTION_ENERGIE',
            'priority': 'HAUTE',
            'action': f"Audit énergétique complet - station consomme {station['total_energy_kwh']:.0f} kWh",
            'savings_potential': '15-25%'
        })
    
    # stations peu efficaces
    bottom_efficiency = ranking['by_efficiency'][-2:]
    for station in bottom_efficiency:
        action_plan.append({
            'station': station['station_name'],
            'type': 'AMELIORATION_EFFICACITE',
            'priority': 'MOYENNE',
            'action': f"Moderniser l'équipement - score efficacité: {station['efficiency_score']}/100",
            'savings_potential': '10-20%'
        })
    
    # stations avec beaucoup d'anomalies
    top_anomalies = ranking['by_anomalies'][:2]
    for station in top_anomalies:
        action_plan.append({
            'station': station['station_name'],
            'type': 'MAINTENANCE',
            'priority': station['priority'],
            'action': f"Inspection technique - {station['anomaly_count']} anomalies détectées",
            'savings_potential': '5-15%'
        })
    
    print(f"✓ {len(action_plan)} actions prioritaires identifiées")
    
    return action_plan

def save_ranking(ranking):
    """
    Sauvegarder le classement
    """
    with open('data/stations_ranking.json', 'w') as f:
        json.dump(ranking, f, indent=2)
    
    print("\n✓ Classement sauvegardé")

def print_summary(ranking):
    """
    Afficher un résumé
    """
    print("\n" + "="*60)
    print("RÉSUMÉ DU CLASSEMENT")
    print("="*60)
    
    print("\nTop 3 stations les plus énergivores:")
    for i, station in enumerate(ranking['by_energy_consumption'][:3]):
        print(f"  {i+1}. {station['station_name']}: {station['total_energy_kwh']:.0f} kWh")
    
    print("\nTop 3 stations les plus efficaces:")
    for i, station in enumerate(ranking['by_efficiency'][:3]):
        print(f"  {i+1}. {station['station_name']}: {station['efficiency_score']}/100")
    
    print("\nStations nécessitant une attention urgente:")
    urgent = [s for s in ranking['by_anomalies'] if s['priority'] == 'URGENTE']
    for station in urgent:
        print(f"  - {station['station_name']}: {station['anomaly_count']} anomalies")

if __name__ == '__main__':
    # générer les données des stations
    stations_data = generate_stations_data()
    
    # classer les stations
    ranking = rank_stations(stations_data)
    
    # générer plan d'action
    action_plan = generate_action_plan(ranking)
    
    # sauvegarder
    save_ranking(ranking)
    
    # afficher résumé
    print_summary(ranking)
    
    print("\n" + "="*60)
    print("MODULE 4 - CLASSEMENT STATIONS TERMINÉ")
    print("="*60)
