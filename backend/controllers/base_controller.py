from utils import get_settings, AppSettings
from utils import PathUtils

class BaseController:

    def __init__(self):
        self.app_settings = get_settings()
        self.path_utils = PathUtils()