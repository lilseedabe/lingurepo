from groq import Groq
from toolhouse import Toolhouse
from lingustruct import LinguStruct

class APIClients:
    def __init__(self, groq_api_key: str, toolhouse_api_key: str, lingu_key: str, user_id: str):
        self.groq = Groq(api_key=groq_api_key)
        self.toolhouse = Toolhouse(api_key=toolhouse_api_key)
        self.toolhouse.set_metadata('id', user_id)
        self.lingu = LinguStruct()