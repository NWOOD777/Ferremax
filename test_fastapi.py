import requests
import json

def test_api():
    print("Testing Ferremax FastAPI endpoints...")
    
    try:
        # Test root endpoint
        response = requests.get("http://localhost:8000/")
        print(f"Root endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test empleados endpoint
        response = requests.get("http://localhost:8000/api/empleados/")
        print(f"\nEmpleados endpoint: {response.status_code}")
        if response.status_code == 200:
            empleados = response.json()
            print(f"Found {len(empleados)} employees")
            if empleados:
                print("\nSample employee data:")
                print(json.dumps(empleados[0], indent=4, ensure_ascii=False))
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the FastAPI server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_api()
