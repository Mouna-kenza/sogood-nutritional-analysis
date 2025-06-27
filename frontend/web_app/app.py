# SoGood Frontend - Mouna
from flask import Flask, render_template, request, jsonify
from tensorflow.keras.models import load_model
import numpy as np
import json
import os

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
    category = request.args.get('category', '')
    nutri_score = request.args.get('nutri_score', '')
    
    # Commencer avec tous les produits
    results = MOCK_PRODUCTS.copy()
    
    # Filtrer par nom/marque si une recherche est tapée
    if query:
        results = [p for p in results if query in p['name'].lower() or query in p['brand'].lower()]
    
    # Filtrer par catégorie si sélectionnée
    if category:
        results = [p for p in results if category in p['category']]
    
    # Filtrer par Nutri-Score si sélectionné
    if nutri_score:
        results = [p for p in results if p['nutri_score'] == nutri_score.upper()]
    
    return jsonify(results)

@app.route('/product/<product_id>')
def product_detail(product_id):
    product = next((p for p in MOCK_PRODUCTS if p['id'] == product_id), None)
    if not product:
        return "Produit non trouvé", 404
    return render_template('product.html', product=product)



# ================================================================ PREDICTIONS 

model_path = os.path.join(os.path.dirname(__file__), "multi_model.h5")

model = load_model(model_path)

nutriscore_map = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e'}

@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        try:
            fields = ['fat_100g', 'sugars_100g', 'salt_100g', 'fiber_100g', 'proteins_100g']
            values = [float(request.form[f]) for f in fields]
            X = np.array([values], dtype='float32')

            pred_nutri, pred_nova, pred_add = model.predict(X)

            nutri = nutriscore_map[pred_nutri.argmax()]
            nova = int(pred_nova.argmax()) + 1
            add = round(float(pred_add[0][0]))

            return render_template("predict.html", prediction=True, nutri=nutri, nova=nova, add=add)
        except Exception as e:
            return f"Erreur : {e}"

    return render_template("predict.html", prediction=False)


if __name__ == '__main__':
    app.run(debug=True)
