from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

# route principale - dashboard
@app.route('/')
def home():
    return render_template('dashboard.html')

# route pour récupérer les KPI
@app.route('/api/kpi')
def get_kpi():
    """
    Retourner les KPI principaux
    """
    try:
        # charger les données
        with open('data/predictions.json', 'r') as f:
            predictions = json.load(f)
        
        with open('data/pump_schedule.json', 'r') as f:
            schedule = json.load(f)
        
        with open('data/anomalies.json', 'r') as f:
            anomalies = json.load(f)
        
        # Charger aussi anomalies ML si disponibles
        ml_anomalies = []
        try:
            with open('data/ml_anomalies.json', 'r') as f:
                ml_anomalies = json.load(f)
        except:
            pass
        
        with open('data/stations_ranking.json', 'r') as f:
            ranking = json.load(f)
        
        # calculer les KPI
        total_energy = sum([s['energy_used'] for s in schedule])
        total_cost = sum([s['cost_fcfa'] for s in schedule])
        nb_anomalies = len(anomalies) + len(ml_anomalies)  # Total hybride
        critical_anomalies = len([a for a in anomalies if a['severity'] == 'CRITIQUE'])
        
        # station la plus énergivore
        top_station = ranking['by_energy_consumption'][0]
        
        kpi = {
            'total_energy_kwh': round(total_energy, 2),
            'total_cost_fcfa': round(total_cost, 2),
            'total_anomalies': nb_anomalies,
            'critical_anomalies': critical_anomalies,
            'top_station_name': top_station['station_name'],
            'top_station_energy': top_station['total_energy_kwh']
        }
        
        return jsonify(kpi)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# route pour les prévisions
@app.route('/api/predictions')
def get_predictions():
    """
    Retourner les données de prévisions
    """
    try:
        with open('data/predictions.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# route pour le planning
@app.route('/api/schedule')
def get_schedule():
    """
    Retourner le planning de pompage
    """
    try:
        with open('data/pump_schedule.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# route pour les anomalies
@app.route('/api/anomalies')
def get_anomalies():
    """
    Retourner les anomalies (HYBRIDE: règles + ML)
    """
    try:
        # Anomalies détectées par règles
        rule_anomalies = []
        try:
            with open('data/anomalies.json', 'r') as f:
                rule_anomalies = json.load(f)
        except:
            pass
        
        # Anomalies détectées par ML
        ml_anomalies = []
        try:
            with open('data/ml_anomalies.json', 'r') as f:
                ml_anomalies = json.load(f)
        except:
            pass
        
        # Stats hybrides
        hybrid_stats = {}
        try:
            with open('data/hybrid_anomalies_stats.json', 'r') as f:
                hybrid_stats = json.load(f)
        except:
            pass
        
        # Retourner structure combinée
        return jsonify({
            'rule_based': rule_anomalies,
            'ml_based': ml_anomalies,
            'stats': hybrid_stats,
            'total': len(rule_anomalies) + len(ml_anomalies)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# route pour le classement
@app.route('/api/ranking')
def get_ranking():
    """
    Retourner le classement des stations
    """
    try:
        with open('data/stations_ranking.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # vérifier que les fichiers existent
    required_files = [
        'data/predictions.json',
        'data/pump_schedule.json',
        'data/anomalies.json',
        'data/stations_ranking.json'
    ]
    
    missing = [f for f in required_files if not os.path.exists(f)]
    
    if missing:
        print("⚠️  Fichiers manquants:")
        for f in missing:
            print(f"   - {f}")
        print("\nLancez d'abord les modules 1-4:")
        print("  python modules/module1_prediction.py")
        print("  python modules/module2_optimization.py")
        print("  python modules/module3_anomalies.py")
        print("  python modules/module4_ranking.py")
    else:
        print("✓ Tous les fichiers sont présents")
        print("\n" + "="*60)
        print("ONEA Energy Optimizer - Dashboard")
        print("="*60)
        print("\nOuvrez votre navigateur sur: http://localhost:5000")
        print("\nAppuyez sur Ctrl+C pour arrêter le serveur")
        print("="*60 + "\n")
        
        app.run(debug=True, host='0.0.0.0', port=5000)
