from flask import Blueprint, flash, redirect, request, url_for

errors_blueprint = Blueprint('errors', __name__)

def check_service_status(error_class):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if not self.status:
                raise error_class("Layer is turned off.")
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

class DomainError(Exception):
    def __init__(self, message="Domain service is currently unavailable. Please try again later."):
        super().__init__(message)
        self.message = message

class DataStorageError(Exception):
    def __init__(self, message="Data storage service is currently unavailable. Please try again later."):
        super().__init__(message)
        self.message = message

class MapperError(Exception):
    def __init__(self, message="Mapper service is currently unavailable. Please try again later."):
        super().__init__(message)
        self.message = message

class AuthenticationError(Exception):
    def __init__(self, message="Authentication service is currently unavailable. Please try again later."):
        super().__init__(message)
        self.message = message 

class ExtractionError(Exception):
    def __init__(self, message="Extraction service is currently unavailable. Please try again later."):
        super().__init__(message)
        self.message = message

class ValidationError(Exception):
    def __init__(self, message="Validation service is currently unavailable. Please try again later."):
        super().__init__(message)
        self.message = message

class AuthorizationError(Exception):
    def __init__(self, message="Authorization service is currently unavailable. Please try again later."):
        super().__init__(message)
        self.message = message

@errors_blueprint.errorhandler(DomainError)
def handle_domain_error(error):
    flash("Domain service is currently unavailable. Please try again later.")
    return redirect(request.url)

@errors_blueprint.errorhandler(DataStorageError)
def handle_data_storage_error(error):
    flash("Data storage service is currently unavailable. Please try again later.")
    return redirect(request.url)

@errors_blueprint.errorhandler(MapperError)
def handle_mapper_error(error):
    flash("Mapper service is currently unavailable. Please try again later.")
    return redirect(request.url)

@errors_blueprint.errorhandler(AuthenticationError)
def handle_authentication_error(error):
    flash("Authentication service is currently unavailable. Please try again later.")
    return redirect(request.url)

@errors_blueprint.errorhandler(ExtractionError)
def handle_extraction_error(error):
    flash("Extraction service is currently unavailable. Please try again later.")
    print("triggered extraction error")
    return redirect(request.url)

@errors_blueprint.errorhandler(ValidationError)
def handle_validation_error(error):
    flash("Validation service is currently unavailable. Please try again later.")
    return redirect(request.url)

@errors_blueprint.errorhandler(AuthorizationError)
def handle_authorization_error(error):
    flash("Authorization service is currently unavailable. Redirected to Home")
    return redirect(url_for('auth.home'))