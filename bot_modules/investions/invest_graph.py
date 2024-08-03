from matplotlib import pyplot as plt
import json
from os.path import dirname, exists


class CourseJsonWriter(object):
    
    def __init__(self, course: int) -> None:
        self.COURSE = course
        self.FILEPATH = f"{dirname(__file__)}//courses.json"
        self.DIRPATH = f"{dirname(__file__)}"
        self.MAX_COURSE_NUMBER = 30
    
    def __read_json_data(self) -> dict:
        """Получает словарь данных из json файла и возвращает словарь с данными.

        Returns:
            dict: Полученный словарь данных из файла json.
        """
        if exists(self.FILEPATH):
            with open(self.FILEPATH, "r", encoding="utf-8") as __file:
                __readed_data: dict = json.load(__file)
            return __readed_data
        else:
            return None
    
    def write_new_course(self) -> None:
        __readed_data: dict = self.__read_json_data()
        ## Получаем последние записанные данные о курсах валюты из json файла.
        __all_courses: list = list(__readed_data.values())[0]
        __all_courses.append(self.COURSE)

        __to_remove = len(__all_courses) - self.MAX_COURSE_NUMBER
        if __to_remove <= 0:
            __to_remove = 0
        
        del __all_courses[:__to_remove]
        self.__write_graph(__all_courses)
        __data_to_write = {
            "courses": __all_courses
            }   
        with open(self.FILEPATH, "w+", encoding="utf-8") as __file:
            json.dump(__data_to_write, __file)
            

    def __write_graph(self, courses: list) -> None:
        plt.clf()  
        x = [i for i in range(1, len(courses) + 1)]
        y = courses
        
        ax = plt.gca()
        ax.spines['top'].set_color('#444444')
        ax.spines['bottom'].set_color('#444444')
        ax.spines['left'].set_color('#444444')
        ax.spines['right'].set_color('#444444')
        plt.xlabel(f'Номер курса от 1 до {self.MAX_COURSE_NUMBER}', color='#76ff7b')
        plt.ylabel('Курс валюты', color='#76ff7b')
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_color('#76ff7b')
        
        plt.gca().set_facecolor("#36393e")
        plt.plot(x, y, color='#76ff7b', marker='o', markersize=7)
        plt.savefig(
            f"{self.DIRPATH}//graph.png",
            bbox_inches='tight',
            pad_inches = 0,
            transparent = True
            )


