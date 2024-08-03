import json
from os import getcwd

class InvestJsonActions:
    
    PATH = getcwd()
    USER_PATH = f'{PATH}//bot_modules//investions//user_invest'
    
    def __init__(self, user_name: str) -> None:
        self.user_name = user_name
    
    def write_user_invest(self, money: float) -> None:
        """Create a new file for the user invest."""
        data = {
            'money': money
        }
        with open(f'{self.USER_PATH}//{self.user_name}.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def read_user_invest(self) -> float:
        '''Read the user invest file, returns the money.'''
        with open(f'{self.USER_PATH}//{self.user_name}.json', 'r', encoding='utf-8') as file:
            data: dict = json.load(file)
        user_invest: float = data.get('money')
        return user_invest

