#!/usr/bin/env python3
"""
Script pour corriger les erreurs de format dans le fichier CSV
Identifie et corrige les lignes mal formatées
"""

import pandas as pd
import sys
import os
from pathlib import Path

def fix_csv_format():
    """Corrige les erreurs de format dans le fichier CSV"""
    
    input_path = "notebooks/fr.openfoodfacts.org.products1.csv"
    output_path = "notebooks/fr.openfoodfacts.org.products1_fixed.csv"
    
    print("🔧 Correction du format CSV")
    print("=" * 50)
    
    if not os.path.exists(input_path):
        print(f"❌ Fichier non trouvé: {input_path}")
        return False
    
    try:
        # Lire le fichier ligne par ligne pour identifier les problèmes
        print("📖 Lecture du fichier ligne par ligne...")
        
        fixed_lines = []
        problematic_lines = []
        line_number = 0
        
        with open(input_path, 'r', encoding='utf-8') as file:
            for line in file:
                line_number += 1
                
                # Compter les tabulations
                tab_count = line.count('\t')
                
                # La première ligne (header) devrait avoir 208 tabulations (209 colonnes)
                if line_number == 1:
                    expected_tabs = 208
                else:
                    expected_tabs = 208  # Basé sur le header
                
                if tab_count != expected_tabs:
                    problematic_lines.append({
                        'line': line_number,
                        'tabs': tab_count,
                        'expected': expected_tabs,
                        'content': line[:100] + "..." if len(line) > 100 else line.strip()
                    })
                    
                    # Essayer de corriger en ajoutant des tabulations manquantes
                    if tab_count < expected_tabs:
                        missing_tabs = expected_tabs - tab_count
                        line = line.rstrip() + '\t' * missing_tabs + '\n'
                    elif tab_count > expected_tabs:
                        # Supprimer les tabulations en trop
                        parts = line.split('\t')
                        if len(parts) > expected_tabs + 1:
                            line = '\t'.join(parts[:expected_tabs + 1]) + '\n'
                
                fixed_lines.append(line)
                
                if line_number % 100000 == 0:
                    print(f"  Lignes traitées: {line_number:,}")
        
        # Écrire le fichier corrigé
        print(f"\n💾 Écriture du fichier corrigé: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as file:
            file.writelines(fixed_lines)
        
        print(f"✅ Fichier corrigé créé avec {len(fixed_lines):,} lignes")
        
        # Afficher les problèmes trouvés
        if problematic_lines:
            print(f"\n⚠️  {len(problematic_lines)} lignes problématiques trouvées:")
            for prob in problematic_lines[:10]:  # Afficher les 10 premiers
                print(f"  Ligne {prob['line']}: {prob['tabs']} tabs (attendu: {prob['expected']})")
                print(f"    Contenu: {prob['content']}")
            if len(problematic_lines) > 10:
                print(f"  ... et {len(problematic_lines) - 10} autres lignes")
        else:
            print("✅ Aucune ligne problématique trouvée")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {e}")
        return False

if __name__ == "__main__":
    success = fix_csv_format()
    sys.exit(0 if success else 1) 