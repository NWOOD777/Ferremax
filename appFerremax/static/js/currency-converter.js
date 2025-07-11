// Script para convertir monedas
let exchangeRate = 850; // Valor predeterminado, 1 USD = 850 CLP
let currentCurrency = 'CLP'; // Moneda por defecto - siempre iniciamos en CLP

// Exponer variables para que otros scripts puedan usarlas
window.exchangeRate = exchangeRate;
window.currentCurrency = currentCurrency;

// Función para obtener el tipo de cambio actual desde nuestra API interna
async function fetchExchangeRate() {
    try {
        const response = await fetch('/api-dolar-json/');
        const data = await response.json();
        
        if (data && data.success && data.exchange_rate) {
            exchangeRate = data.exchange_rate;
            window.exchangeRate = exchangeRate; // Actualizar la variable global
            console.log(`Tipo de cambio actualizado: 1 USD = ${exchangeRate} CLP`);
            // Actualizar el texto del botón para mostrar que los datos están actualizados
            const btnChangeCurrency = document.getElementById('btn-change-currency');
            if (btnChangeCurrency) {
                btnChangeCurrency.classList.remove('btn-outline-primary');
                btnChangeCurrency.classList.add('btn-primary');
            }
            return exchangeRate;
        } else {
            console.error('Error al obtener el tipo de cambio');
            return 850; // Valor por defecto si hay error
        }
    } catch (error) {
        console.error('Error al obtener el tipo de cambio:', error);
        return 850; // Valor por defecto si hay error
    }
}

// Función para identificar elementos de precio en la página
function findPriceElements() {
    // Esta función identifica todos los elementos que contienen precios en la página
    const allElements = document.body.querySelectorAll('*');
    const priceElements = [];
    
    // Expresión regular para detectar formatos de precio (por ejemplo, $1.234, $1,234, $1234)
    const priceRegex = /^\$\s*[\d,.]+(\s*<small>.*<\/small>)?$/;
    
    // Añadir primero los elementos que ya sabemos que son precios
    document.querySelectorAll('.card-text, .product-price').forEach(el => {
        if (!priceElements.includes(el)) {
            priceElements.push(el);
        }
    });
    
    // Buscar elementos con atributo data-price (botones de agregar al carrito, etc)
    document.querySelectorAll('[data-price]').forEach(el => {
        // No convertimos el atributo directamente, pero lo marcamos para cuando
        // se muestre en algún lugar (por ejemplo, en el carrito)
        el.setAttribute('data-original-price', el.getAttribute('data-price'));
    });
    
    // Elementos con formato de precio en su texto pero que no son inputs
    allElements.forEach(el => {
        // Solo procesamos elementos de texto (no inputs, selects, etc)
        if (el.childNodes.length === 1 && 
            el.childNodes[0].nodeType === Node.TEXT_NODE &&
            el.textContent.trim().startsWith('$')) {
            
            const text = el.textContent.trim();
            // Verificar si parece un precio
            if (priceRegex.test(text) && !priceElements.includes(el)) {
                priceElements.push(el);
            }
        }
    });
    
    // Marcar todos los elementos identificados para que sea fácil identificarlos después
    priceElements.forEach(el => {
        if (!el.classList.contains('price-element')) {
            el.classList.add('price-element');
        }
    });
    
    return priceElements;
}

// Función para convertir precios
function convertPrices() {
    // Identificar todos los elementos de precio la primera vez
    findPriceElements();
    
    // Ahora usamos la clase 'price-element' que agregamos para seleccionar todos los elementos de precio
    const priceElements = document.querySelectorAll('.price-element, .card-text, .product-price');
    
    // Buscar el botón activo - primero el nuevo, si no existe usar el anterior
    const currencyToggleBtn = document.getElementById('currency-toggle-btn');
    const btnChangeCurrency = document.getElementById('btn-change-currency');
    
    // Usar el botón que exista
    const activeButton = currencyToggleBtn || btnChangeCurrency;
    
    if (!activeButton) return;
    
    // Configurar manejador de eventos para el botón
    activeButton.addEventListener('click', async function(e) {
        e.preventDefault();
        
        // Mostrar indicador de carga
        const spinner = activeButton.querySelector('.loading-spinner');
        // Para el botón simple sin spans o con estructura moderna
        const isSimpleBtn = activeButton.id === 'currency-toggle-btn';
        
        // Manejar el spinner según el tipo de botón
        if (spinner) {
            if (isSimpleBtn) {
                // Ocultar todo el texto para el botón simple
                activeButton.textContent = '';
                activeButton.appendChild(spinner.cloneNode(true));
                activeButton.lastChild.classList.remove('d-none');
            } else {
                const btnText = activeButton.querySelector('span:first-child');
                if (btnText) {
                    btnText.classList.add('d-none');
                    spinner.classList.remove('d-none');
                }
            }
        }
        
        // Si no tenemos tipo de cambio actualizado, obtenerlo ahora
        if (exchangeRate === 850) {
            await fetchExchangeRate();
        }
        
        if (currentCurrency === 'CLP') {
            // Cambiar a USD
            priceElements.forEach(function(el) {
                // Primero verificamos si el elemento está visible
                if (el.offsetParent !== null) {
                    const priceCLP = parseFloat(el.textContent.replace(/[^\d]/g, ''));
                    if (!isNaN(priceCLP)) {
                        const priceUSD = priceCLP / exchangeRate;
                        el.setAttribute('data-original-price', priceCLP);
                        el.innerHTML = `$${priceUSD.toFixed(2)} <small>USD</small>`;
                    }
                }
            });
            
            // Actualizar todos los elementos con data-price para el carrito
            document.querySelectorAll('[data-price]').forEach(el => {
                const priceCLP = parseFloat(el.getAttribute('data-price'));
                if (!isNaN(priceCLP)) {
                    const priceUSD = priceCLP / exchangeRate;
                    el.setAttribute('data-converted-price', priceUSD.toFixed(2));
                    el.setAttribute('data-currency', 'USD');
                }
            });
            
            // Actualizar texto del botón según tipo
            if (isSimpleBtn) {
                // Para el nuevo diseño de botón con clase currency-text
                const currencyText = activeButton.querySelector('.currency-text');
                if (currencyText) {
                    currencyText.textContent = 'USD';
                } else {
                    activeButton.textContent = 'USD → CLP';
                }
            } else {
                const btnText = activeButton.querySelector('span:first-child');
                if (btnText) btnText.textContent = 'USD → CLP';
            }
            
            currentCurrency = 'USD';
            window.currentCurrency = currentCurrency; // Actualizar la variable global
        } else {
            // Cambiar a CLP
            priceElements.forEach(function(el) {
                // Primero verificamos si el elemento está visible
                if (el.offsetParent !== null) {
                    const originalPrice = el.getAttribute('data-original-price');
                    if (originalPrice) {
                        el.innerHTML = `CLP $${parseInt(originalPrice).toLocaleString('es-CL')}`;
                    } else {
                        // Si no tenemos el precio original guardado, convertir de USD a CLP
                        const priceUSD = parseFloat(el.textContent.replace(/[^\d.]/g, ''));
                        if (!isNaN(priceUSD)) {
                            const priceCLP = priceUSD * exchangeRate;
                            el.innerHTML = `CLP $${Math.round(priceCLP).toLocaleString('es-CL')}`;
                        }
                    }
                }
            });
            
            // Restaurar los precios originales en data-price para el carrito
            document.querySelectorAll('[data-price][data-original-price]').forEach(el => {
                el.removeAttribute('data-converted-price');
                el.removeAttribute('data-currency');
            });
            
            // Actualizar texto del botón según tipo
            if (isSimpleBtn) {
                // Para el nuevo diseño de botón con clase currency-text
                const currencyText = activeButton.querySelector('.currency-text');
                if (currencyText) {
                    currencyText.textContent = 'CLP';
                } else {
                    activeButton.textContent = 'CLP → USD';
                }
            } else {
                const btnText = activeButton.querySelector('span:first-child');
                if (btnText) btnText.textContent = 'CLP → USD';
            }
            currentCurrency = 'CLP';
            window.currentCurrency = currentCurrency; // Actualizar la variable global
        }
        
        // Actualizar los precios en el carrito si está visible
        updateCartPrices();
        
        // Ocultar indicador de carga
        if (spinner) {
            if (isSimpleBtn) {
                // Ya se actualizó el texto del botón completo
                const loadingSpinner = activeButton.querySelector('.loading-spinner');
                if (loadingSpinner) loadingSpinner.remove();
            } else {
                const btnText = activeButton.querySelector('span:first-child');
                if (btnText && spinner) {
                    btnText.classList.remove('d-none');
                    spinner.classList.add('d-none');
                }
            }
        }
    });
}

// Función para actualizar los precios en el carrito según la moneda actual
function updateCartPrices() {
    // Verificar si hay alguna función de actualización de carrito disponible
    if (typeof window.updateCartDisplay === 'function') {
        window.updateCartDisplay();
    }
    
    // Si hay un total o subtotal visible, actualizarlo también
    const totalElements = document.querySelectorAll('.cart-total, .subtotal, .total-price');
    if (totalElements.length > 0) {
        // Recalcular el total basado en los items individuales
        let cart = JSON.parse(localStorage.getItem('cart')) || [];
        let total = 0;
        
        cart.forEach(item => {
            let itemPrice = item.price;
            if (currentCurrency === 'USD' && !isNaN(itemPrice)) {
                itemPrice = itemPrice / exchangeRate;
            }
            total += itemPrice * item.quantity;
        });
        
        // Actualizar los elementos de total
        totalElements.forEach(el => {
            if (currentCurrency === 'USD') {
                el.innerHTML = `$${total.toFixed(2)} <small>USD</small>`;
            } else {
                el.innerHTML = `CLP $${Math.round(total).toLocaleString('es-CL')}`;
            }
        });
    }
}

// Inicializar cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', async function() {
    // Iniciar la carga del tipo de cambio en segundo plano
    fetchExchangeRate();
    
    // Configurar la conversión de precios
    convertPrices();
    
    // Asegurarse de que se usa el botón correcto
    // Si existe currency-toggle-btn (el nuevo) lo usamos, si no buscamos el btn-change-currency (el anterior)
    const currencyToggleBtn = document.getElementById('currency-toggle-btn');
    const btnChangeCurrency = document.getElementById('btn-change-currency');
    
    // Usar el botón que exista
    const activeButton = currencyToggleBtn || btnChangeCurrency;
    
    if (activeButton) {
        if (activeButton.id === 'currency-toggle-btn') {
            // Para botón simple, actualizar directamente
            if (!activeButton.textContent.includes('→')) {
                activeButton.textContent = 'CLP → USD';
            }            } else {
                // Para botón con span, actualizar el span
                const btnText = activeButton.querySelector('span:first-child');
                if (btnText) {
                    btnText.textContent = 'CLP → USD';
                }
            }
    }
    
    // Exponer una función para convertir precios de productos
    window.convertProductPrice = function(product) {
        if (currentCurrency === 'USD') {
            // Si estamos en USD, guardar tanto el precio en USD como el original en CLP
            if (!product.currency || product.currency !== 'USD') {
                product.convertedPrice = product.price / exchangeRate;
                product.originalPrice = product.price;
                product.currency = 'USD';
                // Para mostrar precios en USD, actualizamos el precio
                product.displayPrice = product.convertedPrice.toFixed(2);
            }
        } else {
            // Si estamos en CLP y el producto tenía precio en USD, revertir
            if (product.currency === 'USD' && product.originalPrice) {
                product.displayPrice = product.originalPrice;
            } else {
                product.displayPrice = product.price;
            }
        }
        return product;
    };
});
