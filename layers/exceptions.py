class DomainError(Exception):
    def __init__(self, message="Domain service is currently unavailable. Please try again later."):
        super().__init__(message)

class DataStorageError(Exception):
    def __init__(self, message="Data storage service is currently unavailable. Please try again later."):
        super().__init__(self.message)

class MapperError(Exception):
    def __init__(self, message="Mapper service is currently unavailable. Please try again later."):
        super().__init__(self.message)

class AuthenticationError(Exception):
    def __init__(self, message="Authentication service is currently unavailable. Please try again later."):
        super().__init__(self.message)

class ExtractionError(Exception):
    def __init__(self, message="Extraction service is currently unavailable. Please try again later."):
        super().__init__(self.message)

class ValidationError(Exception):
    def __init__(self, message="Validation service is currently unavailable. Please try again later."):
        super().__init__(self.message)

class AuthorizationError(Exception):
    def __init__(self, message="Authorization service is currently unavailable. Please try again later."):
        super().__init__(self.message)