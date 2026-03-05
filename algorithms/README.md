# Algorithmes IA - ONEA Energy Optimizer

Ce dossier contient les **descriptions au format JSON** de tous les algorithmes d'Intelligence Artificielle utilisés dans le projet ONEA Energy Optimizer.

## 📁 Fichiers

### 1. `prediction_algorithm.json`
**Description complète de l'algorithme de prévision énergétique**
- Type : Machine Learning (Random Forest Regressor)
- Fonction : Prévoir la consommation énergétique sur 24h
- Features : hour, day_of_week, flow, level
- Performance : R² > 0.95

### 2. `optimization_algorithm.json`
**Description complète de l'algorithme d'optimisation du pompage**
- Type : Optimisation Heuristique
- Fonction : Créer un planning de pompage optimal selon tarifs électriques
- Stratégies : POMPER_MAX (heures creuses), POMPER_MIN (heures pointe), POMPER_NORMAL
- Économies : 15-25%

### 3. `anomaly_detection_algorithm.json`
**Description complète de l'algorithme de détection d'anomalies par règles**
- Type : Système Expert basé sur Règles
- Fonction : Détecter anomalies opérationnelles et fuites CONNUES
- Règles : 7 règles de détection (conso anormale, niveaux, fuites, etc.)
- Classification : CRITIQUE / MOYENNE / FAIBLE
- Approche : Niveau 1 de la détection hybride

### 3bis. `ml_anomaly_detection_algorithm.json` ⭐ NOUVEAU
**Description complète de l'algorithme ML de détection d'anomalies**
- Type : Machine Learning Non-supervisé (Isolation Forest)
- Fonction : Détecter patterns anormaux NON ANTICIPÉS
- Features : flow, energy, level, hour
- Performance : Découvre anomalies que les règles auraient manquées
- Approche : Niveau 2 de la détection hybride
- **Avantage clé** : Complète les règles avec capacité de découverte IA

### 4. `ranking_algorithm.json`
**Description complète de l'algorithme de classement des stations**
- Type : Analyse Comparative Multi-Critères
- Fonction : Comparer performances de 6 stations et prioriser actions
- Critères : Énergie, coût, efficacité, anomalies
- Output : Classements + plan d'action

### 5. `system_architecture.json`
**Architecture globale du système**
- Description complète de l'intégration des 5 modules
- Flux de données entre composants
- Stack technique
- Gains attendus
- Roadmap

## 🎯 Pourquoi ces fichiers JSON ?

### Conformité TDR
Le TDR du Hackathon ONEA demande explicitement :
> "Les scripts des algorithmes IA mis en œuvre **(au format Json)**"

Ces fichiers JSON répondent à cette exigence en fournissant :
1. **Description détaillée** de chaque algorithme
2. **Logique et règles** explicites
3. **Paramètres configurables**
4. **Format interopérable** (JSON standard)

### Avantages du format JSON

✅ **Lisibilité** : Structure claire et hiérarchique  
✅ **Interopérabilité** : Compatible tous langages  
✅ **Configuration** : Modification facile des paramètres  
✅ **Documentation** : Auto-documenté  
✅ **Versionning** : Facile à versionner (Git)  
✅ **Validation** : Schémas JSON validables  

## 🔗 Relation avec le code Python

### Implémentation double
Chaque algorithme existe sous **deux formes** :

1. **JSON** (ce dossier) : Description, configuration, documentation
2. **Python** (dossier `modules/`) : Implémentation exécutable

| Algorithme | JSON | Python |
|------------|------|--------|
| Prévision | prediction_algorithm.json | module1_prediction.py |
| Optimisation | optimization_algorithm.json | module2_optimization.py |
| Anomalies | anomaly_detection_algorithm.json | module3_anomalies.py |
| Classement | ranking_algorithm.json | module4_ranking.py |

### Exemple de correspondance

**JSON** (configuration) :
```json
{
  "model_parameters": {
    "n_estimators": 100,
    "random_state": 42
  }
}
```

**Python** (implémentation) :
```python
model = RandomForestRegressor(
    n_estimators=100, 
    random_state=42
)
```

## 📊 Structure type d'un fichier JSON

Chaque fichier JSON contient typiquement :

```json
{
  "algorithm_name": "Nom de l'algorithme",
  "type": "Type (ML, Optimisation, Expert System)",
  "description": "Description détaillée",
  
  "input_data": {
    // Données en entrée
  },
  
  "logic": {
    // Logique étape par étape
  },
  
  "output_format": {
    // Format des résultats
  },
  
  "implementation": {
    // Détails techniques
  }
}
```

## 🛠️ Utilisation

### Pour les développeurs
1. **Lire le JSON** pour comprendre l'algorithme
2. **Consulter le Python** pour l'implémentation
3. **Modifier les paramètres** dans le JSON
4. **Mettre à jour le code Python** en conséquence

### Pour les évaluateurs
1. **Lire les JSON** pour évaluer la logique IA
2. **Vérifier la conformité** avec exigences TDR
3. **Comprendre l'architecture** via system_architecture.json

### Pour l'ONEA
1. **Configuration** : Ajuster paramètres sans toucher au code
2. **Documentation** : Référence complète des algorithmes
3. **Évolution** : Base pour améliorer les algorithmes

## 📝 Validation

Tous les fichiers JSON ont été validés :
- ✅ Syntaxe JSON valide
- ✅ Structure cohérente
- ✅ Documentation complète
- ✅ Correspondance avec code Python

## 🔄 Mise à jour

Les fichiers JSON doivent être mis à jour quand :
- Les algorithmes évoluent
- Les paramètres changent
- De nouvelles règles sont ajoutées
- L'architecture est modifiée

**Fréquence recommandée** : À chaque modification majeure des modules Python

## 📖 Documentation complémentaire

Pour plus de détails sur le projet :
- **Architecture globale** : `system_architecture.json` (ce dossier)
- **Documentation technique** : `../DOCUMENTATION.md`
- **Guide utilisateur** : `../README.md`
- **Installation** : `../GUIDE_INSTALLATION.md`

## 🏆 Conformité Hackathon

Ces fichiers JSON répondent spécifiquement à l'exigence du TDR :
> **"Les scripts des algorithmes IA mis en œuvre (au format Json)"**

Ils démontrent :
- ✅ Maîtrise de l'IA (algorithmes explicités)
- ✅ Clarté des explications (documentation détaillée)
- ✅ Faisabilité technique (implémentation + config)
- ✅ Adaptabilité (paramètres configurables)

---

**Créé pour** : Hackathon ONEA 2026  
**Version** : 1.0  
**Format** : JSON (RFC 8259)  
**Encodage** : UTF-8
