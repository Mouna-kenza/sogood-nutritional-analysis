from flask import Flask, render_template, request, jsonify, Response
import json
import requests
import pandas as pd
from datetime import datetime
from tensorflow.keras.models import load_model
import numpy as np
import os


app = Flask(__name__)

API_BASE_URL = "http://localhost:8000/api"

# Catégories disponibles pour le filtrage
CATEGORIES = [
    "Condiments",
    "Épices", 
    "Viandes",
    "Céréales",
    "Légumes",
    "Fruits",
    "Produits laitiers",
    "Boissons",
    "Snacks",
    "Desserts",
    "Conserves",
    "Fruits secs",
    "Poissons",
    "Œufs",
    "Huiles",
    "Soupes",
    "Pâtes",
    "Riz",
    "Farines",
    "Sucre",
    "Plats préparés"
]

@app.route('/')
def home():
    """Page d'accueil avec recherche de produits"""
    # Charger automatiquement les produits au chargement de la page
    query = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    category = request.args.get('category', '')
    
    # Construire l'URL de l'API
    api_url = f"{API_BASE_URL}/products/search"
    params = {
        'q': query,
        'page': page,
        'page_size': 20
    }
    
    if category:
        params['category'] = category
    
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        products = data.get('products', [])
        total_products = data.get('total', 0)
        total_pages = data.get('total_pages', 1)
        
        # Calculer les pages à afficher
        start_page = max(1, page - 2)
        end_page = min(total_pages, page + 2)
        
        return render_template('index.html', 
                             products=products, 
                             query=query,
                             category=category,
                             categories=CATEGORIES,
                             current_page=page,
                             total_pages=total_pages,
                             start_page=start_page,
                             end_page=end_page,
                             total_products=total_products)
    except requests.RequestException as e:
        print(f"Erreur API: {e}")
        return render_template('index.html', 
                             products=[], 
                             query=query,
                             category=category,
                             categories=CATEGORIES,
                             error="Erreur de connexion à l'API")

@app.route('/dashboard')
def dashboard():
    """Page du tableau de bord Power BI"""
    return render_template('dashboard.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    category = request.args.get('category', '')
    
    # Construire l'URL de l'API
    api_url = f"{API_BASE_URL}/products/search"
    params = {
        'q': query,
        'page': page,
        'page_size': 20
    }
    
    if category:
        params['category'] = category
    
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        products = data.get('products', [])
        total_products = data.get('total', 0)
        total_pages = data.get('total_pages', 1)
        
        # Calculer les pages à afficher
        start_page = max(1, page - 2)
        end_page = min(total_pages, page + 2)
        
        return render_template('index.html', 
                             products=products, 
                             query=query,
                             category=category,
                             categories=CATEGORIES,
                             current_page=page,
                             total_pages=total_pages,
                             start_page=start_page,
                             end_page=end_page,
                             total_products=total_products)
    except requests.RequestException as e:
        print(f"Erreur API: {e}")
        return render_template('index.html', 
                             products=[], 
                             query=query,
                             category=category,
                             categories=CATEGORIES,
                             error="Erreur de connexion à l'API")

@app.route('/product/<product_id>')
def product_detail(product_id):
    """Page de détail d'un produit"""
    try:
        response = requests.get(f"{API_BASE_URL}/products/{product_id}")
        
        if response.status_code == 200:
            product = response.json()
            return render_template('product.html', product=product)
        else:
            return "Produit non trouvé", 404
            
    except Exception as e:
        print(f"Erreur lors de la récupération du produit: {e}")
        return "Erreur lors de la récupération du produit", 500

@app.route('/api/stats/overview')
def get_stats_overview():
    """Statistiques générales de la base de données"""
    try:
        response = requests.get(f"{API_BASE_URL}/stats/overview")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({})
    except Exception as e:
        print(f"Erreur lors de la récupération des stats: {e}")
        return jsonify({})

@app.route('/api/stats/categories')
def get_stats_categories():
    """Statistiques par catégorie"""
    try:
        response = requests.get(f"{API_BASE_URL}/stats/categories")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({})
    except Exception as e:
        print(f"Erreur lors de la récupération des stats catégories: {e}")
        return jsonify({})

@app.route('/api/stats/brands')
def get_stats_brands():
    """Statistiques par marque"""
    try:
        response = requests.get(f"{API_BASE_URL}/stats/brands")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({})
    except Exception as e:
        print(f"Erreur lors de la récupération des stats marques: {e}")
        return jsonify({})

@app.route('/api/stats/nutrition')
def get_stats_nutrition():
    """Statistiques nutritionnelles"""
    try:
        response = requests.get(f"{API_BASE_URL}/stats/nutrition")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({})
    except Exception as e:
        print(f"Erreur lors de la récupération des stats nutrition: {e}")
        return jsonify({})

@app.route('/api/stats/export-csv')
def export_csv():
    """Export des données en CSV pour Power BI"""
    try:
        # Récupérer tous les produits
        all_products = []
        page = 1
        page_size = 1000
        
        while True:
            response = requests.get(f"{API_BASE_URL}/products/search", params={
                'q': '',
                'page': page,
                'page_size': page_size
            })
            
            if response.status_code != 200:
                break
                
            data = response.json()
            products = data.get('products', [])
            
            if not products:
                break
                
            all_products.extend(products)
            
            if len(products) < page_size:
                break
                
            page += 1
        
        if not all_products:
            return jsonify({"error": "Aucun produit trouvé"}), 404
        
        # Créer le DataFrame
        df = pd.DataFrame(all_products)
        
        # Nettoyer les données
        df['category'] = df['category'].fillna('Non classé')
        df['brand'] = df['brand'].fillna('Marque inconnue')
        df['nutri_score'] = df['nutri_score'].fillna('N/A')
        df['nova_score'] = df['nova_score'].fillna(0)
        
        # Créer des colonnes calculées
        df['has_image'] = df['image_url'].notna().astype(int)
        df['has_front_image'] = df['image_front_url'].notna().astype(int)
        df['has_nutrition_data'] = df['energy_100g'].notna().astype(int)
        df['quality_score'] = 5  # Score de base
        
        # Générer le CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_content = df.to_csv(index=False, encoding='utf-8')
        
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=sogood_products_{timestamp}.csv'}
        )
        
    except Exception as e:
        print(f"Erreur lors de l'export CSV: {e}")
        return jsonify({"error": "Erreur lors de l'export"}), 500

@app.route('/api/stats')
def get_stats():
    """Statistiques de la base de données (ancienne route)"""
    try:
        response = requests.get(f"{API_BASE_URL}/products/stats/database")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({})
    except Exception as e:
        print(f"Erreur lors de la récupération des stats: {e}")
        return jsonify({})



# # ================================================================ PREDICTIONS 

# model_path = os.path.join(os.path.dirname(__file__), "multi_model.h5")

# model = load_model(model_path)

# nutriscore_map = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e'}

# @app.route("/predict", methods=["GET", "POST"])
# def predict():
#     if request.method == "POST":
#         try:
#             fields = ['fat_100g', 'sugars_100g', 'salt_100g', 'fiber_100g', 'proteins_100g']
#             values = [float(request.form[f]) for f in fields]
#             X = np.array([values], dtype='float32')

#             pred_nutri, pred_nova, pred_add = model.predict(X)

#             nutri = nutriscore_map[pred_nutri.argmax()]
#             nova = int(pred_nova.argmax()) + 1
#             add = round(float(pred_add[0][0]))

#             return render_template("predict.html", prediction=True, nutri=nutri, nova=nova, add=add)
#         except Exception as e:
#             return f"Erreur : {e}"

#     return render_template("predict.html", prediction=False)


# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)
