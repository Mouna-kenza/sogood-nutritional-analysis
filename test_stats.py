import requests
import json

def test_stats_endpoint():
    """Test de l'endpoint de statistiques"""
    try:
        # Test de l'endpoint health
        response = requests.get("http://localhost:8000/health")
        print(f"Health endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test de l'endpoint stats
        response = requests.get("http://localhost:8000/api/stats/overview")
        print(f"\nStats endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_stats_endpoint() 