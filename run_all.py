#!/usr/bin/env python3
"""
Script pour lancer automatiquement tout le projet ONEA Energy Optimizer
"""
import os
import sys
import subprocess
import time

def print_banner():
    print("\n" + "="*70)
    print("  ⚡ ONEA ENERGY OPTIMIZER - Hackathon 2026")
    print("="*70 + "\n")

def run_module(module_name, script_path):
    """
    Exécuter un module et afficher le résultat
    """
    print(f"\n{'='*70}")
    print(f"  Exécution : {module_name}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=False,
            text=True,
            check=True
        )
        print(f"✓ {module_name} terminé avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Erreur lors de l'exécution de {module_name}")
        print(f"  Code erreur: {e.returncode}")
        return False
    except Exception as e:
        print(f"✗ Erreur: {str(e)}")
        return False

def check_dependencies():
    """
    Vérifier que les dépendances sont installées
    """
    print("Vérification des dépendances...")
    
    required_packages = [
        'flask',
        'numpy',
        'pandas',
        'sklearn',
        'joblib'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            if package == 'sklearn':
                # sklearn s'importe comme sklearn mais s'installe comme scikit-learn
                try:
                    __import__('sklearn')
                except ImportError:
                    missing.append('scikit-learn')
            else:
                missing.append(package)
    
    if missing:
        print(f"\n⚠️  Paquets manquants: {', '.join(missing)}")
        print("\nInstallez-les avec:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    print("✓ Toutes les dépendances sont installées\n")
    return True

def main():
    print_banner()
    
    # vérifier les dépendances
    if not check_dependencies():
        sys.exit(1)
    
    # liste des modules à exécuter
    modules = [
        ("Module 1 - Prévision énergétique", "modules/module1_prediction.py"),
        ("Module 2 - Optimisation du pompage", "modules/module2_optimization.py"),
        ("Module 3 - Détection anomalies HYBRIDE (Règles + ML)", "modules/module3_anomalies.py"),
        ("Module 4 - Classement des stations", "modules/module4_ranking.py")
    ]
    
    # exécuter chaque module
    success_count = 0
    for name, path in modules:
        if run_module(name, path):
            success_count += 1
            time.sleep(1)  # petit délai entre les modules
    
    print("\n" + "="*70)
    print(f"  RÉSUMÉ: {success_count}/{len(modules)} modules exécutés avec succès")
    print("="*70)
    
    if success_count == len(modules):
        print("\n✓ Tous les modules ont été exécutés avec succès!")
        print("\nVous pouvez maintenant lancer le dashboard:")
        print("  python app.py")
        print("\nPuis ouvrir: http://localhost:5000")
        
        # demander si on lance le dashboard
        print("\n" + "-"*70)
        response = input("Voulez-vous lancer le dashboard maintenant ? (o/n): ")
        
        if response.lower() in ['o', 'oui', 'y', 'yes']:
            print("\nLancement du dashboard...")
            print("Appuyez sur Ctrl+C pour arrêter\n")
            time.sleep(2)
            
            try:
                subprocess.run([sys.executable, "app.py"])
            except KeyboardInterrupt:
                print("\n\nDashboard arrêté.")
        else:
            print("\nPour lancer le dashboard plus tard:")
            print("  python app.py")
    else:
        print("\n⚠️  Certains modules ont échoué. Vérifiez les erreurs ci-dessus.")
        sys.exit(1)

if __name__ == '__main__':
    main()
