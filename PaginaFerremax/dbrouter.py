class PaymentMethodRouter:
    """
    A router to control database operations on payment-related models.
    """
    payment_models = ['metodo_pago', 'estado_pago']
    
    def db_for_read(self, model, **hints):
        if model._meta.model_name.lower() in self.payment_models:
            # Use Oracle database for payment methods and payment statuses
            return 'oracle'
        # Use default database for everything else
        return 'default'
    
    def db_for_write(self, model, **hints):
        if model._meta.model_name.lower() in self.payment_models:
            # Use Oracle database for payment methods and payment statuses
            return 'oracle'
        # Use default database for everything else
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        # Allow relations between objects in all databases
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Allow all models to be migrated in all databases
        return True
