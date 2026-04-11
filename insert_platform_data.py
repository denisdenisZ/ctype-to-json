import json


def insert_platform_data(stdout: str, json_data: str) -> dict:
    info = {}
    for line in stdout.splitlines():
        key, value = line.rsplit(" ", 1)
        info[key] = int(value)

    for type_name, entry in json_data.items():
        if entry["kind"] == "struct":
            entry["size"] = info.get(type_name)
            for field in entry["fields"]:
                field["offset"] = info.get(f'{type_name}.{field["name"]}')
                field["size"] = info.get(
                    f'{type_name}.{field["name"]}.size'
                )

    return json_data


def insert_platform_data_from_file(stdout: str, json_data: str) -> dict:
    with open(json_data) as f:
        data = json.load(f)

    data = insert_platform_data(stdout, data)

    return data
