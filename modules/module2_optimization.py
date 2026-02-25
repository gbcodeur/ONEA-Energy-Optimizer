import json
import numpy as np
from datetime import datetime, timedelta

def get_electricity_price(hour):
    """
    Retourner le prix de l'électricité selon l'heure
    Tarifs SONABEL officiels - Type E2 Industriel (Moyenne Tension)
    Grille tarifaire du 1er octobre 2023
    """
    # heures pleines: 00h-17h (54 FCFA/kWh)
    if hour < 17:
        return 54
    # heures de pointe: 17h-24h (118 FCFA/kWh)
    else:
        return 118

def optimize_pumping():
    """
    Créer un planning de pompage optimisé
    """
    print("Optimisation du planning de pompage...")
    
    # charger les prévisions
    with open('data/predictions.json', 'r') as f:
        predictions = json.load(f)
    
    pump_plan = []
    current_level = 65  # niveau actuel du réservoir
    
    for pred in predictions:
        hour = pred['hour']
        energy = pred['energy_predicted']
        flow = pred.get('flow_estimated', 120)  # valeur par défaut si absent
        
        # prix électricité
        price = get_electricity_price(hour)
        
        # décision de pompage
        # STRATÉGIE OPTIMALE SONABEL:
        # - Avant 17h (54 FCFA): pomper au maximum pour remplir réservoir
        # - Après 17h (118 FCFA): minimiser au strict nécessaire
        
        # si heures pleines (avant 17h) ET niveau < 85% -> pomper à fond
        if price == 54 and current_level < 85:
            pump_action = "POMPER_MAX"
            pump_rate = 100  # 100% capacité
            flow_actual = flow * 1.3
            
        # si heures de pointe (après 17h) ET niveau > 25% -> pomper minimum
        elif price == 118 and current_level > 25:
            pump_action = "POMPER_MIN"
            pump_rate = 25  # 25% capacité seulement
            flow_actual = flow * 0.4
            
        # si heures de pointe MAIS niveau critique < 25% -> pomper normal (sécurité)
        elif price == 118 and current_level <= 25:
            pump_action = "POMPER_URGENCE"
            pump_rate = 60  # 60% pour remonter niveau
            flow_actual = flow * 0.8
            
        # sinon normal (transition ou niveau optimal)
        else:
            pump_action = "POMPER_NORMAL"
            pump_rate = 70  # 70% capacité
            flow_actual = flow
        
        # calculer nouveau niveau (simplifié)
        # le niveau augmente si on pompe, baisse si on consomme
        level_change = (flow_actual - 120) / 10  # 120 = conso moyenne
        current_level += level_change
        current_level = max(25, min(95, current_level))
        
        # coût
        cost = energy * (pump_rate / 100) * price
        
        pump_plan.append({
            'date': pred['date'],
            'hour': hour,
            'pump_action': pump_action,
            'pump_rate': pump_rate,
            'price_kwh': price,
            'energy_used': round(energy * (pump_rate / 100), 2),
            'cost_fcfa': round(cost, 2),
            'level_after': round(current_level, 2)
        })
    
    # sauvegarder
    with open('data/pump_schedule.json', 'w') as f:
        json.dump(pump_plan, f, indent=2)
    
    # stats
    total_cost = sum([p['cost_fcfa'] for p in pump_plan])
    total_energy = sum([p['energy_used'] for p in pump_plan])
    
    # calculer coût sans optimisation
    cost_no_optim = sum([pred['energy_predicted'] * get_electricity_price(pred['hour']) 
                         for pred in predictions])
    
    savings = cost_no_optim - total_cost
    savings_percent = (savings / cost_no_optim) * 100
    
    print(f"\n✓ Planning généré pour 24h")
    print(f"  - Énergie totale: {total_energy:.2f} kWh")
    print(f"  - Coût optimisé: {total_cost:.2f} FCFA")
    print(f"  - Coût sans optim: {cost_no_optim:.2f} FCFA")
    print(f"  - Économies: {savings:.2f} FCFA ({savings_percent:.1f}%)")
    
    return pump_plan

def generate_summary():
    """
    Résumé de l'optimisation
    """
    with open('data/pump_schedule.json', 'r') as f:
        plan = json.load(f)
    
    summary = {
        'total_hours': len(plan),
        'total_energy_kwh': sum([p['energy_used'] for p in plan]),
        'total_cost_fcfa': sum([p['cost_fcfa'] for p in plan]),
        'avg_pump_rate': np.mean([p['pump_rate'] for p in plan]),
        'hours_peak': len([p for p in plan if p['pump_action'] == 'POMPER_MAX']),
        'hours_low': len([p for p in plan if p['pump_action'] == 'POMPER_MIN']),
        'hours_normal': len([p for p in plan if p['pump_action'] == 'POMPER_NORMAL'])
    }
    
    return summary

if __name__ == '__main__':
    pump_plan = optimize_pumping()
    summary = generate_summary()
    
    print("\n" + "="*50)
    print("MODULE 2 - OPTIMISATION TERMINÉ")
    print("="*50)
    print(f"Pompage MAX: {summary['hours_peak']}h")
    print(f"Pompage NORMAL: {summary['hours_normal']}h")
    print(f"Pompage MIN: {summary['hours_low']}h")
