import json

from flat_price.models.complexes import Flat


with open('flats.backup.json', 'r', encoding="utf-8") as file:
    data_str = file.read()
    data_json = json.loads(data_str)

    flats = {}
    for flat_json in data_json:
        flat = Flat.model_validate(flat_json)
        flat.price = flat_json['price_history'][-1]['price']
        flat.status = flat_json['status_history'][-1]['status']
        flats[flat.id] = flat


result = [json.loads(flat.model_dump_json()) for flat in flats.values()]
with open('flats.json', 'w', encoding="utf-8") as file:
    file.write(json.dumps(result, indent=4, ensure_ascii=False))