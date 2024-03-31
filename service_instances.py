from services.authentication import Authentication
from services.mapper import Mapper
from services.extraction import Extraction
from services.data_storage import DataStorage
from services.validation import Validation
from services.domain import Domain

authentication = Authentication()
mapper = Mapper()
extraction = Extraction()
datastorage = DataStorage()
validation = Validation()
domain = Domain()