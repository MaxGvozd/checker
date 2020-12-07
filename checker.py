import json, logging, os, sys

logging.basicConfig(level=logging.DEBUG, filename='checker.log', format='%(asctime)s || %(levelname)s:%(message)s')    

analogous_types = {
    'string': str,
    'integer': int,
    'number': (int, float),
    'object': dict,
    'array': list,
    'boolean': bool,
    'null': type(None)
    }
extension = [".schema", ".json"]
obj_schema = {}
obj_data = []

class JSON_File:    
    def __init__(self, path, name, extension):        
        self.path = path
        self.name = name
        self.extension = extension
        self.data = self.open_json()        

    def open_json(self):
        with open(self.path) as f:
            file = f.read()
            data = json.loads(file)
            f.close()
        if isinstance(data, dict):
            return data
        else:
            logging.debug(f'Содержимое файла: "{self.path}" не соответствует формату JSON.')
            return None
    

class Schema(JSON_File):
    pass       


class Data_JSON(JSON_File):
    pass


def find_files(path):
    global obj_data, obj_schema
    if os.path.isdir(path):
        listdir = os.listdir(path)
        for file in listdir:
            find_files(f'{path}\\{file}')
    else:        
        if os.path.isfile(path) and path.lower().endswith(extension[0]):
            obj_schema[os.path.basename(path).lower().rstrip(extension[0])] = Schema(path, path.lower().rstrip(extension[0]), extension[0])
        elif os.path.isfile(path) and path.lower().endswith(extension[1]):
            obj_data.append(Data_JSON(path, path.lower().rstrip(extension[1]), extension[1]))
        else:
            logging.debug(f'Присутствует неподходящий формат файла: {path}.') 


def validation():
    for i in obj_data:
        logging.debug(f'Файл: "{i.path}."')
        try:
            if i.data:
                schema = obj_schema.get(i.data['event'])                
            else:
                continue
        except:
            logging.error(f'JSON схема "{i.data["event"]}" для данных JSON "{i.path}" не обнаружена!')
            schema = []
        if schema:
            valid_schema(schema.data, i.data)            
        else:
            logging.error(f'JSON схема "{i.data["event"]}" для данных JSON "{i.path}" не обнаружена!')

        logging.debug(f'Проверка файла "{i.path}" закончена.')


def valid_required(required, data):
    return [name for name in required if name not in data]


def valid_properties(properties, data):
    try:
        for field in data.keys():
            if isinstance(properties.get(field)['type'], list):
                if type(data[field]) not in [analogous_types[name] for name in properties.get(field)['type']]:
                    return False
                elif isinstance(properties.get(field)['type'], str):
                    if properties.get(field)['type'] == "object":
                        valid_schema(properties[field], data, field)
                    elif properties.get(field)['type'] == "array":
                        if len(data[field]):
                            valid_schema(properties[field]['items'], data, field, array=True)
                        elif type(data[field]) != analogous_types[properties.get(field)['type']]:
                            return False
                    else:
                        return True
                else:
                    return True
    except:
        logging.error(f'В данных JSON ошибка типа данных!')


def valid_schema(schema, data, column='data', array=False):
    if schema.get('type') != "object":
        return "This is not object!"
    required = schema.get("required")
    if array:
        try:
            keys = data.get(column)[0].keys()
        except:
            logging.error(f'В данных JSON ошибка данных!')
    else:
        try:
            keys = data.get(column).keys()
        except:
            logging.error(f'В данных JSON ошибка данных!')
    try:
        check_required = valid_required(required, keys)
    except:
        logging.error(f'В данных JSON ошибка обязательных полей согласно схемы "schema.path"!')
        check_required = []
    if check_required:
	    logging.error(f'В данных JSON ошибка обязательных полей согласно схемы "schema.path"!')	    
    chema_prop = schema.get("properties")
    if array:
	    check_properties = valid_properties(chema_prop, data.get(column)[0])
    else:
	    check_properties = valid_properties(chema_prop, data.get(column))
    if check_properties:
	    logging.error(f'В данных JSON ошибка обязательных полей согласно схемы "schema.path"!')    
                    

if __name__ == "__main__":
    try:
        logging.debug(f'Запуск скрипта. Путь: "{sys.argv[1]}."   ' + "+" * 8)
        find_files(sys.argv[1])        
    except IndexError:
        logging.error(f'При вызове скрипта не объялен аргумент!')
    validation()
    
