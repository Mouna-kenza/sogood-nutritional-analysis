import requests
import pandas as pd
import json
from datetime import datetime
import os

def export_products_to_csv():
    """Exporte tous les produits de la base de données vers un CSV pour Power BI"""
    
    print("📊 EXPORT DES DONNÉES POUR POWER BI")
    print("=" * 50)
    
    # Récupérer le nombre total de produits
    response = requests.get("http://localhost:8000/api/products/search?q=&page=1&page_size=1")
    data = response.json()
    total_products = data.get('total', 0)
    
    print(f"Nombre total de produits à exporter: {total_products:,}")
    
    all_products = []
    page = 1
    page_size = 1000  # Récupérer 1000 produits par page
    
    while True:
        print(f"📥 Récupération page {page}...")
        
        response = requests.get(f"http://localhost:8000/api/products/search?q=&page={page}&page_size={page_size}")
        data = response.json()
        products = data.get('products', [])
        
        if not products:
            break
            
        all_products.extend(products)
        print(f"✅ {len(products)} produits récupérés (total: {len(all_products)})")
        
        if len(products) < page_size:
            break
            
        page += 1
    
    print(f"\n📋 Traitement de {len(all_products)} produits...")
    
    if not all_products:
        print("❌ Aucun produit récupéré")
        return None, None
    
    # Convertir en DataFrame
    df = pd.DataFrame(all_products)
    
    # Nettoyer et standardiser les données
    df = clean_dataframe(df)
    
    # Sauvegarder en CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sogood_products_{timestamp}.csv"
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    df.to_csv(filepath, index=False, encoding='utf-8')
    
    print(f"✅ Fichier CSV créé: {filename}")
    print(f"📁 Chemin: {filepath}")
    print(f"📊 {len(df)} produits exportés")
    
    # Afficher quelques statistiques
    print(f"\n📈 STATISTIQUES RAPIDES:")
    print(f"-" * 30)
    print(f"Catégories uniques: {df['category'].nunique()}")
    print(f"Marques uniques: {df['brand'].nunique()}")
    print(f"Nutri-Scores: {df['nutri_score'].value_counts().to_dict()}")
    print(f"Produits avec images: {df['image_url'].notna().sum()}")
    
    return filepath, df

def clean_dataframe(df):
    """Nettoie et standardise le DataFrame"""
    
    # Remplacer les valeurs manquantes
    df['category'] = df['category'].fillna('Non classé')
    df['brand'] = df['brand'].fillna('Marque inconnue')
    df['nutri_score'] = df['nutri_score'].fillna('N/A')
    df['nova_score'] = df['nova_score'].fillna(0)
    
    # Nettoyer les catégories
    df['category'] = df['category'].replace({
        'undefined': 'Non classé',
        'Plant-based foods and beverages': 'Aliments et boissons végétaux',
        'Dairies': 'Produits laitiers',
        'Meals': 'Plats préparés',
        'Beverages': 'Boissons',
        'Desserts': 'Desserts',
        'Salted snacks': 'Snacks salés'
    })
    
    # Standardiser les Nutri-Scores
    df['nutri_score'] = df['nutri_score'].str.upper()
    
    # Créer des colonnes calculées
    df['has_image'] = df['image_url'].notna().astype(int)
    df['has_front_image'] = df['image_front_url'].notna().astype(int)
    df['has_nutrition_data'] = df['energy_100g'].notna().astype(int)
    
    # Score de qualité simple
    df['quality_score'] = 5
    
    return df

def generate_statistics():
    """Génère des statistiques pour l'API"""
    
    print("📊 GÉNÉRATION DES STATISTIQUES")
    print("=" * 40)
    
    # Récupérer un échantillon pour les statistiques
    response = requests.get("http://localhost:8000/api/products/search?q=&page=1&page_size=1000")
    data = response.json()
    products = data.get('products', [])
    
    if not products:
        return {}
    
    df = pd.DataFrame(products)
    df = clean_dataframe(df)
    
    stats = {
        'total_products': len(df),
        'categories': df['category'].value_counts().head(10).to_dict(),
        'nutri_scores': df['nutri_score'].value_counts().to_dict(),
        'brands': df['brand'].value_counts().head(10).to_dict(),
        'quality_stats': {
            'with_images': int(df['has_image'].sum()),
            'with_nutrition_data': int(df['has_nutrition_data'].sum()),
            'with_brand_info': int((df['brand'] != 'Marque inconnue').sum()),
            'with_category_info': int((df['category'] != 'Non classé').sum())
        },
        'nova_scores': df['nova_score'].value_counts().to_dict(),
        'avg_energy': float(df['energy_100g'].mean()) if df['energy_100g'].notna().any() else 0,
        'avg_fat': float(df['fat_100g'].mean()) if df['fat_100g'].notna().any() else 0,
        'avg_proteins': float(df['proteins_100g'].mean()) if df['proteins_100g'].notna().any() else 0,
        'avg_sugar': float(df['sugar_100g'].mean()) if df['sugar_100g'].notna().any() else 0,
        'avg_salt': float(df['salt_100g'].mean()) if df['salt_100g'].notna().any() else 0
    }
    
    print("✅ Statistiques générées")
    return stats

if __name__ == "__main__":
    try:
        # Exporter les données
        filepath, df = export_products_to_csv()
        
        # Générer les statistiques
        stats = generate_statistics()
        
        # Sauvegarder les statistiques en JSON
        stats_file = os.path.join(os.path.dirname(__file__), 'statistics.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Statistiques sauvegardées: {stats_file}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc() 