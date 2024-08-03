import json
import random
from os import getcwd

class InvestJsonActions:
    
    PATH = getcwd()
    USER_PATH = f'{PATH}//bot_modules//investions//user_invest'
    
    def __init__(self) -> None:
        pass
    
    def write_course_invest(self, course: float) -> None:
        """Create a new file for the user invest."""
        data = {
            'course': course
        }
        with open(f'{self.PATH}//bot_modules//investions//course.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def read_course_invest(self) -> float:
        """Read invest course."""
        with open(f'{self.PATH}//bot_modules//investions//course.json', 'r', encoding='utf-8') as file:
            data: dict = json.load(file)
        course: float = data.get('course')
        return course
    
    def set_new_course(self) -> None:
        old_course = self.read_course_invest()
        deviation = random.random()
        basic_chance = 0.5
        if old_course <= 113:
            basic_chance -= 0.05
        elif old_course >= 314:
            basic_chance += 0.05
        else:
            basic_chance = 0.5
            
        if deviation >= basic_chance:
            new_course = round(old_course + (old_course * (random.random() * random.random() * 0.08)), 2)
            self.write_course_invest(new_course)
        else:
            new_course = round(old_course - (old_course * (random.random() * random.random() * 0.08)), 2)
            self.write_course_invest(new_course)
            

if __name__ == '__main__':
    class_invest = InvestJsonActions()
    print(class_invest.set_new_course())