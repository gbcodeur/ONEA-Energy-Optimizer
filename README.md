# ONEA Energy Optimizer - Hackathon Project

## Description
Système d'optimisation énergétique pour l'ONEA (Office National de l'Eau et de l'Assainissement).
Ce projet utilise l'IA pour réduire la consommation électrique, optimiser le pompage et détecter les anomalies.

## Modules
1. **Prévision énergétique** - Prédiction de la consommation sur 24h
2. **Optimisation du pompage** - Planning intelligent basé sur les heures creuses
3. **Détection d'anomalies** - Identification des comportements anormaux
4. **Classement des stations** - Comparaison des performances énergétiques
5. **Dashboard Web** - Interface de visualisation complète

## Installation

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

## Utilisation

### 1. Générer les données et entraîner les modèles
```bash
python modules/module1_prediction.py
python modules/module2_optimization.py
python modules/module3_anomalies.py
python modules/module4_ranking.py
```

### 2. Lancer le dashboard
```bash
python app.py
```

Puis ouvrir http://localhost:5000 dans votre navigateur.

## Structure du projet
```
onea_energy_optimizer/
├── app.py                      # Application Flask
├── requirements.txt            # Dépendances Python
├── modules/
│   ├── module1_prediction.py   # Prévision énergétique
│   ├── module2_optimization.py # Optimisation pompage
│   ├── module3_anomalies.py    # Détection anomalies
│   └── module4_ranking.py      # Classement stations
├── data/
│   ├── historical_data.json    # Données historiques
│   ├── predictions.json        # Prévisions
│   ├── pump_schedule.json      # Planning pompage
│   ├── anomalies.json          # Anomalies détectées
│   └── stations_ranking.json   # Classement stations
├── models/
│   └── energy_model.pkl        # Modèle ML sauvegardé
├── templates/
│   └── dashboard.html          # Interface web
└── static/
    ├── style.css               # Styles CSS
    └── charts.js               # Graphiques JS
```

## Auteur
Développé pour le hackathon ONEA 2026
