"""
Test PDF Export Functionality for Ferremax

This script tests the page loading and verifies key elements that should be present
in the pagos.html template, particularly for the PDF export functionality.

Usage:
    python test_pdf_export.py

Requirements:
    - Django
    - requests
    - beautifulsoup4
"""
import os
import sys
import requests
from bs4 import BeautifulSoup
import django
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PaginaFerremax.settings")
django.setup()

# Import Django models
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

def check_server_status():
    """Check if the Django server is running"""
    try:
        response = requests.get("http://127.0.0.1:8000/")
        if response.status_code == 200:
            logging.info("✅ Django server is running")
            return True
        else:
            logging.error(f"❌ Django server returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logging.error("❌ Django server is not running. Please start it with 'python manage.py runserver'")
        return False

def check_pdf_export_elements():
    """Test the PDF export functionality elements"""
    client = Client()
    
    # Create a test admin user if it doesn't exist
    if not User.objects.filter(username="testadmin").exists():
        User.objects.create_superuser(username="testadmin", email="test@example.com", password="testpassword")
        logging.info("Created test admin user")
    
    # Login
    logged_in = client.login(username="testadmin", password="testpassword")
    if not logged_in:
        logging.error("❌ Failed to log in as test admin")
        return False
    
    # Create a session with admin privileges
    session = client.session
    session['nombre_usuario'] = "Admin Test"
    session['tipo_usuario'] = "Administrador"
    session.save()
    
    # Access the pagos view
    response = client.get("/pagos/")
    
    if response.status_code != 200:
        logging.error(f"❌ Failed to access pagos view. Status code: {response.status_code}")
        return False
    
    # Parse the HTML response
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Check for necessary elements
    elements_to_check = {
        "Balance Report Div": soup.find(id="balanceReporte"),
        "Download PDF Button": soup.find(id="btnImprimirPDF"),
        "PDF JavaScript": soup.find("script", string=lambda text: text and "html2canvas" in text if text else False),
        "Table Elements": soup.find("table", id="tablaTransacciones")
    }
    
    # Report results
    all_passed = True
    for name, element in elements_to_check.items():
        if element:
            logging.info(f"✅ {name} found in the page")
        else:
            logging.error(f"❌ {name} NOT found in the page")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    logging.info("Starting PDF export functionality test...")
    
    if check_server_status():
        if check_pdf_export_elements():
            logging.info("🎉 All PDF export elements are present in the page")
            logging.info("The PDF export functionality appears to be set up correctly")
        else:
            logging.warning("⚠️ Some PDF export elements are missing. Please check the pagos.html template")
    else:
        logging.error("Please start the Django server before running this test")
    
    logging.info("Test completed")
