import os
import django
import sys

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PaginaFerremax.settings")
django.setup()

from appFerremax.models import Producto, Sucursal
from django.core.files.base import ContentFile
from django.conf import settings
from PIL import Image
import io

def test_media_handling():
    # 1. Check if media directory exists and create if needed
    media_dir = settings.MEDIA_ROOT
    productos_dir = os.path.join(media_dir, 'productos')
    
    print(f"Media root: {media_dir}")
    print(f"Media URL: {settings.MEDIA_URL}")
    print(f"Debug mode: {settings.DEBUG}")
    
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)
        print(f"Created media directory: {media_dir}")
    else:
        print(f"Media directory exists: {media_dir}")
    
    if not os.path.exists(productos_dir):
        os.makedirs(productos_dir)
        print(f"Created productos directory: {productos_dir}")
    else:
        print(f"Productos directory exists: {productos_dir}")
    
    # 2. List any existing product images
    products_with_images = Producto.objects.filter(imagen__isnull=False)
    print(f"Found {products_with_images.count()} products with images")
    
    for product in products_with_images[:5]:
        print(f"Product: {product.nombre_producto}")
        print(f"  Image path: {product.imagen.name}")
        print(f"  Image URL: {product.imagen.url}")
        print(f"  Image exists: {os.path.exists(os.path.join(settings.MEDIA_ROOT, product.imagen.name))}")
    
    # 3. Create a test image
    try:
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color = 'red')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_content = ContentFile(img_io.getvalue(), name='test_image.jpg')
        
        # Create a test product with this image
        sucursal = Sucursal.objects.first()
        if not sucursal:
            print("Error: No sucursales found in database")
            return
        
        test_product = Producto(
            nombre_producto="Test Media Product",
            descripcion="Test product for media handling",
            marca="Test",
            precio_unitario=1000,
            stock_total=10,
            sucursal=sucursal,
            imagen=img_content
        )
        test_product.save()
        
        print(f"Created test product with ID: {test_product.id_producto}")
        print(f"Image path: {test_product.imagen.name}")
        print(f"Image URL: {test_product.imagen.url}")
        print(f"Image exists: {os.path.exists(os.path.join(settings.MEDIA_ROOT, test_product.imagen.name))}")
        
        # Delete the test product to clean up
        test_product.delete()
        print("Test product deleted")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_media_handling()
