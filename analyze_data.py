import requests
import json
from collections import Counter

def analyze_products():
    """Analyse les produits dans la base de données"""
    
    print("🔍 Connexion à l'API...")
    
    # Récupérer le nombre total de produits
    response = requests.get("http://localhost:8000/api/products/search?q=&page=1&page_size=1")
    data = response.json()
    total_products = data.get('total', 0)
    
    print(f"📊 ANALYSE DE LA BASE DE DONNÉES")
    print(f"=" * 50)
    print(f"Nombre total de produits: {total_products:,}")
    
    # Récupérer un échantillon de produits pour analyser les catégories
    print("📥 Récupération d'un échantillon de produits...")
    response = requests.get("http://localhost:8000/api/products/search?q=&page=1&page_size=100")
    data = response.json()
    products = data.get('products', [])
    
    print(f"✅ {len(products)} produits récupérés")
    
    if products:
        # Analyser les catégories
        categories = [p.get('category', 'Non classé') for p in products]
        category_counts = Counter(categories)
        
        print(f"\n🏷️  CATÉGORIES (échantillon de {len(products)} produits):")
        print(f"-" * 40)
        
        # Afficher les 20 catégories les plus fréquentes
        for category, count in category_counts.most_common(20):
            percentage = (count / len(products)) * 100
            print(f"{category}: {count} produits ({percentage:.1f}%)")
        
        # Analyser les Nutri-Scores
        nutriscores = [p.get('nutri_score', 'N/A') for p in products]
        nutriscore_counts = Counter(nutriscores)
        
        print(f"\n🥗 NUTRI-SCORES (échantillon de {len(products)} produits):")
        print(f"-" * 40)
        
        for grade, count in nutriscore_counts.most_common():
            percentage = (count / len(products)) * 100
            print(f"{grade}: {count} produits ({percentage:.1f}%)")
        
        # Analyser les marques
        brands = [p.get('brand', 'N/A') for p in products if p.get('brand')]
        brand_counts = Counter(brands)
        
        print(f"\n🏭 MARQUES (top 10, échantillon de {len(products)} produits):")
        print(f"-" * 40)
        
        for brand, count in brand_counts.most_common(10):
            percentage = (count / len(products)) * 100
            print(f"{brand}: {count} produits ({percentage:.1f}%)")
        
        # Statistiques sur les images
        products_with_images = sum(1 for p in products if p.get('image_url'))
        products_with_front_images = sum(1 for p in products if p.get('image_front_url'))
        
        print(f"\n🖼️  IMAGES (échantillon de {len(products)} produits):")
        print(f"-" * 40)
        print(f"Produits avec image_url: {products_with_images} ({products_with_images/len(products)*100:.1f}%)")
        print(f"Produits avec image_front_url: {products_with_front_images} ({products_with_front_images/len(products)*100:.1f}%)")
        
        # Statistiques sur les données nutritionnelles
        products_with_energy = sum(1 for p in products if p.get('energy_100g') is not None)
        products_with_fat = sum(1 for p in products if p.get('fat_100g') is not None)
        products_with_proteins = sum(1 for p in products if p.get('proteins_100g') is not None)
        
        print(f"\n📈 DONNÉES NUTRITIONNELLES (échantillon de {len(products)} produits):")
        print(f"-" * 40)
        print(f"Produits avec énergie/100g: {products_with_energy} ({products_with_energy/len(products)*100:.1f}%)")
        print(f"Produits avec matières grasses/100g: {products_with_fat} ({products_with_fat/len(products)*100:.1f}%)")
        print(f"Produits avec protéines/100g: {products_with_proteins} ({products_with_proteins/len(products)*100:.1f}%)")
        
        # Afficher un exemple de produit
        if products:
            print(f"\n📋 EXEMPLE DE PRODUIT:")
            print(f"-" * 40)
            example = products[0]
            print(f"ID: {example.get('id')}")
            print(f"Nom: {example.get('name')}")
            print(f"Marque: {example.get('brand')}")
            print(f"Catégorie: {example.get('category')}")
            print(f"Nutri-Score: {example.get('nutri_score')}")
            print(f"NOVA: {example.get('nova_score')}")

if __name__ == "__main__":
    try:
        analyze_products()
    except requests.exceptions.ConnectionError:
        print("❌ Erreur: Impossible de se connecter à l'API. Assurez-vous que le backend est démarré.")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc() 