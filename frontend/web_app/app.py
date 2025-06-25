# SoGood Frontend - Mouna
from flask import Flask, render_template, request, jsonify
import json
import requests

app = Flask(__name__)

API_BASE_URL = "http://localhost:8000/api/v1"

@app.route('/')
def home():
    """Page d'accueil avec recherche de produits"""
    return render_template('index.html')

@app.route('/search')
def search():
    """Recherche de produits via l'API backend"""
    try:
        params = {
            'q': request.args.get('q', ''),
            'category': request.args.get('category', ''),
            'nutri_score': request.args.get('nutri_score', ''),
            'complete_data': 'false',  # Désactivé par défaut pour afficher tous les produits
            'page': request.args.get('page', 1),
            'page_size': 50
        }
        
        # Appel à l'API backend
        response = requests.get(f"{API_BASE_URL}/products/search", params=params)
        
        if response.status_code == 200:
            data = response.json()
            # Retourner le format complet attendu par le JavaScript
            return jsonify({
                'products': data['products'],
                'total': data['total'],
                'page': data['page'],
                'total_pages': data['total_pages']
            })
        else:
            return jsonify({
                'products': [],
                'total': 0,
                'page': 1,
                'total_pages': 0
            })
            
    except Exception as e:
        print(f"Erreur lors de la recherche: {e}")
        return jsonify({
            'products': [],
            'total': 0,
            'page': 1,
            'total_pages': 0
        })

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

@app.route('/api/stats')
def get_stats():
    """Statistiques de la base de données"""
    try:
        response = requests.get(f"{API_BASE_URL}/products/stats/database")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({})
    except Exception as e:
        print(f"Erreur lors de la récupération des stats: {e}")
        return jsonify({})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
