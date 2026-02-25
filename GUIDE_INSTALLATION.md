# Guide d'Installation et d'Utilisation

## Installation Rapide

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

#### 1. Télécharger le projet
```bash
# Si vous avez le fichier zip
unzip onea_energy_optimizer.zip
cd onea_energy_optimizer

# Ou cloner depuis git (si applicable)
git clone [URL_DU_REPO]
cd onea_energy_optimizer
```

#### 2. Créer un environnement virtuel
```bash
# Sur Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Sur Windows
python -m venv venv
venv\Scripts\activate
```

#### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

## Utilisation

### Étape 1 : Générer les données et entraîner les modèles

Exécuter les 4 modules dans l'ordre :

```bash
# Module 1 - Prévision énergétique
python modules/module1_prediction.py

# Module 2 - Optimisation du pompage
python modules/module2_optimization.py

# Module 3 - Détection d'anomalies
python modules/module3_anomalies.py

# Module 4 - Classement des stations
python modules/module4_ranking.py
```

**Résultat attendu** :
- Création du dossier `data/` avec 4 fichiers JSON
- Création du dossier `models/` avec le modèle ML
- Affichage des statistiques dans le terminal

### Étape 2 : Lancer le dashboard

```bash
python app.py
```

**Résultat** :
```
✓ Tous les fichiers sont présents

============================================================
ONEA Energy Optimizer - Dashboard
============================================================

Ouvrez votre navigateur sur: http://localhost:5000

Appuyez sur Ctrl+C pour arrêter le serveur
============================================================
```

### Étape 3 : Accéder au dashboard

Ouvrir votre navigateur et aller sur : **http://localhost:5000**

Vous devriez voir :
- 4 KPI en haut (Énergie, Coût, Anomalies, Top Station)
- 4 graphiques interactifs

## Fichiers générés

Après exécution des modules, vous aurez :

```
data/
├── historical_data.json      # 30 jours de données historiques
├── predictions.json          # Prévisions pour 24h
├── pump_schedule.json        # Planning de pompage optimisé
├── anomalies.json           # Anomalies détectées
└── stations_ranking.json    # Classement des stations

models/
└── energy_model.pkl         # Modèle ML entraîné
```

## Commandes utiles

### Tout exécuter d'un coup (Linux/Mac)
```bash
python modules/module1_prediction.py && \
python modules/module2_optimization.py && \
python modules/module3_anomalies.py && \
python modules/module4_ranking.py && \
python app.py
```

### Tout exécuter d'un coup (Windows)
```cmd
python modules/module1_prediction.py & python modules/module2_optimization.py & python modules/module3_anomalies.py & python modules/module4_ranking.py & python app.py
```

### Script automatique
Créer un fichier `run.sh` (Linux/Mac) :
```bash
#!/bin/bash
echo "Génération des données..."
python modules/module1_prediction.py
python modules/module2_optimization.py
python modules/module3_anomalies.py
python modules/module4_ranking.py
echo "Lancement du dashboard..."
python app.py
```

Puis :
```bash
chmod +x run.sh
./run.sh
```

## Dépannage

### Erreur : Module not found
```bash
# Vérifier que l'environnement virtuel est activé
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Réinstaller les dépendances
pip install -r requirements.txt
```

### Erreur : Port 5000 déjà utilisé
Modifier le port dans `app.py` :
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Changer 5000 en 5001
```

### Erreur : Fichiers manquants
Relancer les modules 1-4 :
```bash
python modules/module1_prediction.py
python modules/module2_optimization.py
python modules/module3_anomalies.py
python modules/module4_ranking.py
```

### Dashboard vide
1. Ouvrir la console du navigateur (F12)
2. Vérifier les erreurs JavaScript
3. Vérifier que Flask tourne bien
4. Vérifier que les fichiers JSON existent dans `data/`

## Configuration avancée

### Modifier les paramètres de simulation

**Nombre de jours de données** (module1_prediction.py) :
```python
for day in range(30):  # Changer 30 en 60 pour 2 mois
```

**Tarifs électricité** (module2_optimization.py) :
```python
def get_electricity_price(hour):
    if hour >= 22 or hour < 6:
        return 50  # Modifier le prix heures creuses
    elif 6 <= hour < 18:
        return 75  # Modifier le prix heures normales
    else:
        return 100  # Modifier le prix heures de pointe
```

**Seuils d'anomalies** (module3_anomalies.py) :
```python
if energy_diff > 30:  # Changer 30 pour ajuster sensibilité
    alert_list.append("CONSO_ANORMALE")
```

## API Endpoints

Le serveur Flask expose plusieurs endpoints :

- `GET /` - Dashboard principal
- `GET /api/kpi` - KPI principaux (JSON)
- `GET /api/predictions` - Prévisions (JSON)
- `GET /api/schedule` - Planning pompage (JSON)
- `GET /api/anomalies` - Anomalies (JSON)
- `GET /api/ranking` - Classement stations (JSON)

Exemple d'utilisation :
```bash
curl http://localhost:5000/api/kpi
```

## Support

Pour toute question :
1. Vérifier la documentation : `DOCUMENTATION.md`
2. Consulter le README : `README.md`
3. Vérifier les logs dans le terminal

## Améliorations possibles

- Ajouter authentification utilisateur
- Sauvegarder l'historique des optimisations
- Exporter les rapports en PDF
- Ajouter notifications par email
- Intégrer données météo réelles
- Connecter à de vrais capteurs IoT
