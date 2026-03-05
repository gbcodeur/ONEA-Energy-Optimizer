import json
import numpy as np

def generate_stations_data():
    print("Génération des données multi-stations (Impact Carbone & Mix Énergétique)...")
    
    stations =[
        {'id': 'ST_01', 'name': 'Ouagadougou Pissy', 'capacity': 500, 'solar_equipped': True},
        {'id': 'ST_02', 'name': 'Ouaga Ziga', 'capacity': 1000, 'solar_equipped': True},
        {'id': 'ST_03', 'name': 'Ouaga Sud', 'capacity': 350, 'solar_equipped': False},
        {'id': 'ST_04', 'name': 'Bobo Nasso', 'capacity': 600, 'solar_equipped': True},
        {'id': 'ST_05', 'name': 'Koudougou', 'capacity': 300, 'solar_equipped': False},
        {'id': 'ST_06', 'name': 'Banfora', 'capacity': 250, 'solar_equipped': False}
    ]
    
    stations_data =[]
    
    for station in stations:
        # Volumes hebdomadaires
        total_flow = station['capacity'] * 24 * 7 * np.random.uniform(0.6, 0.9)
        total_energy = total_flow * 0.8 / np.random.uniform(0.7, 1.0)
        
        # Mix Énergétique simulé
        if station['solar_equipped']:
            solar_pct = np.random.uniform(0.15, 0.35) # 15% à 35% d'énergie solaire
            gasoil_pct = np.random.uniform(0.02, 0.05) # Peu de coupures
        else:
            solar_pct = 0
            gasoil_pct = np.random.uniform(0.08, 0.15) # Forte dépendance au groupe électrogène
            
        sonabel_pct = 1 - solar_pct - gasoil_pct
        
        # Calcul des kWh
        solar_kwh = total_energy * solar_pct
        sonabel_kwh = total_energy * sonabel_pct
        gasoil_kwh = total_energy * gasoil_pct
        
        # Coûts et Impact (Hypothèses ONEA)
        cost_sonabel = sonabel_kwh * 85  # Prix moyen lissé
        liters_gasoil = gasoil_kwh / 3.0
        cost_gasoil = liters_gasoil * 675
        
        co2_emissions = liters_gasoil * 2.6
        total_cost = cost_sonabel + cost_gasoil
        
        stations_data.append({
            'id': station['id'],
            'name': station['name'],
            'total_flow_m3': round(total_flow, 0),
            'total_energy_kwh': round(total_energy, 0),
            'solar_coverage_pct': round(solar_pct * 100, 1),
            'gasoil_liters': round(liters_gasoil, 0),
            'co2_emissions_kg': round(co2_emissions, 0),
            'total_cost_fcfa': round(total_cost, 0),
            'cost_per_m3': round(total_cost / total_flow, 2)
        })
        
    return stations_data

def rank_stations(stations_data):
    print("\nClassement des stations...")
    
    # 1. Les plus gros pollueurs (CO2 et Gasoil)
    by_carbon = sorted(stations_data, key=lambda x: x['co2_emissions_kg'], reverse=True)
    
    # 2. Les champions du Solaire
    by_solar = sorted(stations_data, key=lambda x: x['solar_coverage_pct'], reverse=True)
    
    # 3. Les plus coûteuses au m3 produit
    by_cost_efficiency = sorted(stations_data, key=lambda x: x['cost_per_m3'], reverse=True)
    
    ranking = {
        'by_carbon_footprint':[
            {
                'rank': i+1, 'station_name': s['name'], 
                'co2_emissions_kg': s['co2_emissions_kg'],
                'gasoil_liters': s['gasoil_liters'],
                'alert': 'URGENCE_TRANSITION_SOLAIRE' if i < 2 else 'NORMAL'
            } for i, s in enumerate(by_carbon)
        ],
        'by_solar_efficiency':[
            {
                'rank': i+1, 'station_name': s['name'], 
                'solar_coverage_pct': s['solar_coverage_pct']
            } for i, s in enumerate(by_solar)
        ],
        'by_cost_efficiency': [
            {
                'rank': i+1, 'station_name': s['name'], 
                'cost_per_m3': s['cost_per_m3']
            } for i, s in enumerate(by_cost_efficiency)
        ],
        'detailed_data': stations_data
    }
    
    with open('data/stations_ranking.json', 'w') as f:
        json.dump(ranking, f, indent=2)
        
    print(" Classement sauvegardé (Focus Carbone et Solaire)")
    return ranking

if __name__ == '__main__':
    data = generate_stations_data()
    rank_stations(data)
    print("="*50 + "\nMODULE 4 TERMINÉ\n" + "="*50)