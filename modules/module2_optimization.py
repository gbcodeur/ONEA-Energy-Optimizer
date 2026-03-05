import json
import numpy as np
from datetime import datetime

# --- CONSTANTES ONEA (Tirées du document technique) ---
TARIF_SONABEL_HP = 118      # Heures de pointe (17h-24h) FCFA/kWh
TARIF_SONABEL_HC = 54       # Heures pleines (00h-17h) FCFA/kWh
PRIX_GASOIL_LITRE = 675     # FCFA par litre de gasoil (Arrêté 2022)
KWH_PER_LITER = 3.0         # 1 litre de gasoil produit environ 3 kWh
EMISSION_CO2_LITRE = 2.6    # kg de CO2 par litre de gasoil
MAX_POWER_SONABEL = 90      # kW max autorisés par la SONABEL avant pénalité

def get_sonabel_price(hour):
    return TARIF_SONABEL_HC if hour < 17 else TARIF_SONABEL_HP

def optimize_pumping():
    print("Optimisation du Mix Énergétique (Solaire / SONABEL / Groupe Électrogène)...")
    
    with open('data/predictions.json', 'r') as f:
        predictions = json.load(f)
        
    pump_plan =[]
    current_level = 65  # Niveau initial du château d'eau (%)
    
    for pred in predictions:
        hour = pred['hour']
        energy_needed = pred['energy_predicted']
        flow_estimated = pred['flow_estimated']
        solar_available = pred['solar_capacity_predicted']
        grid_ok = pred['grid_status_predicted'] == 1
        
        sonabel_price = get_sonabel_price(hour)
        
        # --- 1. DÉCISION DU NIVEAU DE POMPAGE (Peak Shaving & Tarifs) ---
        if solar_available > 50 and current_level < 90:
            pump_action = "POMPER_MAX (Solaire Gratuit)"
            pump_rate = 100
            flow_actual = flow_estimated * 1.3
        elif grid_ok and sonabel_price == 54 and current_level < 85:
            pump_action = "POMPER_NORMAL (SONABEL HC)"
            pump_rate = 80  # Limité à 80% pour éviter pénalité de puissance
            flow_actual = flow_estimated * 1.1
        elif grid_ok and sonabel_price == 118 and current_level > 35:
            pump_action = "POMPER_MIN (Esquive Pointe)"
            pump_rate = 25
            flow_actual = flow_estimated * 0.4
        elif not grid_ok and current_level > 25:
            pump_action = "MAINTIEN_VITAL (Coupure Réseau)"
            pump_rate = 15  # Sur groupe électrogène, on fait le strict minimum
            flow_actual = flow_estimated * 0.2
        else: # Urgence (niveau critique)
            pump_action = "URGENCE_RESERVOIR_BAS"
            pump_rate = 60
            flow_actual = flow_estimated * 0.8
            
        energy_used = energy_needed * (pump_rate / 100)
        
        # --- 2. RÉPARTITION DU MIX ÉNERGÉTIQUE (Le cœur de l'optimisation) ---
        energy_from_solar = 0
        energy_from_sonabel = 0
        energy_from_generator = 0
        
        energy_remaining = energy_used
        
        # Priorité 1 : Solaire (0 FCFA)
        if solar_available > 0:
            energy_from_solar = min(energy_remaining, solar_available)
            energy_remaining -= energy_from_solar
            
        # Priorité 2 : SONABEL
        if energy_remaining > 0 and grid_ok:
            # On limite la SONABEL à MAX_POWER_SONABEL pour éviter les pénalités
            energy_from_sonabel = min(energy_remaining, MAX_POWER_SONABEL)
            energy_remaining -= energy_from_sonabel
            if energy_from_sonabel >= MAX_POWER_SONABEL:
                pump_action += " [ALERTE PÉNALITÉ ÉVITÉE]"
                
        # Priorité 3 : Groupe électrogène (Dernier recours car très cher et polluant)
        if energy_remaining > 0:
            energy_from_generator = energy_remaining
            
        # --- 3. CALCUL DES COÛTS ET DE L'IMPACT CARBONE ---
        cost_solar = 0
        cost_sonabel = energy_from_sonabel * sonabel_price
        gasoil_liters = energy_from_generator / KWH_PER_LITER
        cost_generator = gasoil_liters * PRIX_GASOIL_LITRE
        
        total_cost = cost_solar + cost_sonabel + cost_generator
        co2_emissions = gasoil_liters * EMISSION_CO2_LITRE
        
        # Simulation niveau réservoir
        consumption_rate = 120 
        level_change = (flow_actual - consumption_rate) / 10
        current_level = max(25, min(95, current_level + level_change))
        
        pump_plan.append({
            'date': pred['date'],
            'hour': hour,
            'pump_action': pump_action,
            'pump_rate': pump_rate,
            'energy_used': round(energy_used, 2),
            # Mix Énergétique
            'mix_solar_kwh': round(energy_from_solar, 2),
            'mix_sonabel_kwh': round(energy_from_sonabel, 2),
            'mix_generator_kwh': round(energy_from_generator, 2),
            # Coûts et Impact
            'cost_fcfa': round(total_cost, 2),
            'gasoil_used_liters': round(gasoil_liters, 2),
            'co2_emissions_kg': round(co2_emissions, 2),
            'reservoir_level': round(current_level, 1),
            'grid_status': "OK" if grid_ok else "COUPURE"
        })
        
    with open('data/pump_schedule.json', 'w') as f:
        json.dump(pump_plan, f, indent=2)
        
    # --- 4. STATISTIQUES ET MÉTRIQUES POUR LE JURY ---
    total_cost = sum([p['cost_fcfa'] for p in pump_plan])
    total_solar = sum([p['mix_solar_kwh'] for p in pump_plan])
    total_gasoil_liters = sum([p['gasoil_used_liters'] for p in pump_plan])
    total_co2 = sum([p['co2_emissions_kg'] for p in pump_plan])
    
    # Calcul des économies (Si l'ONEA avait tout pompé à la demande, sans Solaire ni optimisation)
    cost_no_optim = sum([pred['energy_predicted'] * get_sonabel_price(pred['hour']) for pred in predictions])
    savings = cost_no_optim - total_cost
    
    print(f"\n Mix Énergétique calculé sur 24h :")
    print(f"    Solaire gratuit exploité : {total_solar:.1f} kWh")
    print(f"    Gasoil consommé : {total_gasoil_liters:.1f} Litres")
    print(f"    Empreinte CO2 : {total_co2:.1f} kg")
    print(f"\n Bilan Financier :")
    print(f"  - Coût Optimisé : {total_cost:.0f} FCFA")
    print(f"  - Coût Sans Optim : {cost_no_optim:.0f} FCFA")
    print(f"  - Économies : {savings:.0f} FCFA ({(savings/cost_no_optim)*100:.1f}%)")
    
    return pump_plan

if __name__ == '__main__':
    optimize_pumping()
    print("="*50 + "\nMODULE 2 TERMINÉ\n" + "="*50)