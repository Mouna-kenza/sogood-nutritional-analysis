# SoGood Frontend - Mouna
from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# Données mock pour commencer
MOCK_PRODUCTS = [
    {
        'id': '1', 'name': 'Nutella', 'brand': 'Ferrero',
        'category': 'Pâtes à tartiner', 'nutri_score': 'E', 'nova_score': 4,
        'sugar_100g': 56.3, 'salt_100g': 0.107, 'energy_100g': 539,
        'controversies': ['Très riche en sucre', 'Riche en graisses saturées']
    },
    {
        'id': '2', 'name': 'Evian', 'brand': 'Evian', 
        'category': 'Eaux', 'nutri_score': 'A', 'nova_score': 1,
        'sugar_100g': 0, 'salt_100g': 0, 'energy_100g': 0,
        'controversies': []
    },
    {
        'id': '3', 'name': 'Chips Lay\'s', 'brand': 'Lay\'s',
        'category': 'Snacks', 'nutri_score': 'D', 'nova_score': 3, 
        'sugar_100g': 0.5, 'salt_100g': 1.6, 'energy_100g': 540,
        'controversies': ['Riche en sel']
    }
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    results = [p for p in MOCK_PRODUCTS if query in p['name'].lower()]
    return jsonify(results)

@app.route('/product/<product_id>')
def product_detail(product_id):
    product = next((p for p in MOCK_PRODUCTS if p['id'] == product_id), None)
    if not product:
        return "Produit non trouvé", 404
    return render_template('product.html', product=product)

if __name__ == '__main__':
    app.run(debug=True)
