from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('dashboard_pro.html')

@app.route('/api/kpi')
def get_kpi():
    try:
        with open('data/predictions.json', 'r') as f:
            predictions = json.load(f)
        with open('data/pump_schedule.json', 'r') as f:
            schedule = json.load(f)
        with open('data/anomalies.json', 'r') as f:
            anomalies = json.load(f)
            
        ml_anomalies =[]
        if os.path.exists('data/ml_anomalies.json'):
            with open('data/ml_anomalies.json', 'r') as f:
                ml_anomalies = json.load(f)

        # NOUVEAUX KPIs (Mix Énergétique & Impact Carbone)
        total_cost = sum([s.get('cost_fcfa', 0) for s in schedule])
        total_solar = sum([s.get('mix_solar_kwh', 0) for s in schedule])
        total_gasoil = sum([s.get('gasoil_used_liters', 0) for s in schedule])
        total_co2 = sum([s.get('co2_emissions_kg', 0) for s in schedule])
        
        # Calcul des économies (Si 100% SONABEL sans optimisation)
        cost_no_optim = sum([p['energy_predicted'] * (54 if p['hour'] < 17 else 118) for p in predictions])
        savings = cost_no_optim - total_cost

        kpi = {
            'total_cost_fcfa': round(total_cost, 0),
            'savings_fcfa': round(savings, 0),
            'savings_percent': round((savings/cost_no_optim)*100, 1) if cost_no_optim > 0 else 0,
            'total_solar_kwh': round(total_solar, 0),
            'total_gasoil_liters': round(total_gasoil, 1),
            'total_co2_kg': round(total_co2, 1),
            'total_anomalies': len(anomalies) + len(ml_anomalies),
            'critical_anomalies': len([a for a in anomalies if a.get('severity') == 'CRITIQUE'])
        }
        return jsonify(kpi)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions')
def get_predictions():
    with open('data/predictions.json', 'r') as f: return jsonify(json.load(f))

@app.route('/api/schedule')
def get_schedule():
    with open('data/pump_schedule.json', 'r') as f: return jsonify(json.load(f))

@app.route('/api/anomalies')
def get_anomalies():
    rule_anomalies = json.load(open('data/anomalies.json')) if os.path.exists('data/anomalies.json') else[]
    ml_anomalies = json.load(open('data/ml_anomalies.json')) if os.path.exists('data/ml_anomalies.json') else[]
    return jsonify({'rule_based': rule_anomalies, 'ml_based': ml_anomalies})

@app.route('/api/ranking')
def get_ranking():
    with open('data/stations_ranking.json', 'r') as f: return jsonify(json.load(f))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)