from os import walk, getcwd, listdir, path
from json import load, dump
from zipfile import is_zipfile, ZipFile

def read(file1: str) -> dict:
    with open(file=f"{getcwd()}/{file1}", mode="r", encoding="utf-8") as f:
        return load(f)

def write(path_to_json: str, data: dict) -> None:
    with open(file=f"{getcwd()}/{path_to_json}", mode="w", encoding="utf-8") as sett:
        dump(data, sett, indent=3, ensure_ascii=False)


def open_pack(path: str) -> list[list[str]]:
    files = []
    if is_zipfile(path):
        z = ZipFile("Pepeland Pack v.1.12.zip")

        for file in z.namelist():
            if ".properties" in file:
                with z.open(file) as myfile:
                    files.append(str(myfile.read()).replace("b'", "").replace("'", "").split("\\r\\n"))
        return files
    
    for root, _, files1 in walk(path):
        for file in files1:
            if ".properties" in file:
                with open(f"{root}\\{file}") as file_properties:
                    files.append(file_properties.read().split("\n"))
    
    return files

# -------------------------------------------------------------------------------------------------------------
colonel_settings = read("colonel_settings/colonel_settings.json")


resource_pack_name_part_to_search = colonel_settings["resource_pack_name_part_to_search"]

raw_command = colonel_settings["raw_command"]
semi_command = colonel_settings["item"]

items_places = colonel_settings["items_places"]

armor_parts = colonel_settings["armor_parts"]
armor_order = colonel_settings["armor_order"]


# -------------------------------------------------------------------------------------------------------------
path_to_ids = "/colonel_settings/items_ids.json"
items_ids = read(path_to_ids)


# -------------------------------------------------------------------------------------------------------------
output_settings = read("colonel_settings/output_settings.json")

space_betwean_costumes_rows = output_settings["space_betwean_costume_rows"] + 1
space_betwean_costumes_columns = output_settings["space_betwean_columns"]

space_betwean_armor_stands_in_rows = output_settings["space_betwean_armor_stands_in_rows"]

rows = output_settings["costumes_in_columns"]


# -------------------------------------------------------------------------------------------------------------
def get_costume_optifine_name(file: list[str]) -> str:
    for line in file:
        if "=" not in line:
            continue
        key = line.lower().split("=")[0]
        if "name" in key:
            return line.split("ipattern:")[-1] or "_"
    return "_"

def get_costume_items(file: list[str]) -> list[str]:
    for line in file:
        if "=" not in line:
            continue
        key = line.lower().split("=")[0]
        if "items" in key:
            return line.split("=")[-1].split(" ")
    return None

def sort_costume_armor(unsorted_items: list[str]):
    temp_dict = {}
    not_armor = []
    main_list = []
    
    for armor_material in armor_order:
        for item in unsorted_items:
            if item in armor_parts:
                if armor_material in item:
                    if armor_material not in temp_dict.keys():
                        temp_dict[armor_material] = []
                    temp_dict[armor_material].append(item)
                
    for item in unsorted_items:
        if item not in armor_parts:
            not_armor.append([item])
    
    main_list = list(temp_dict.values())
    if len(not_armor) != 0:
        main_list += not_armor
    
    
    return main_list, len(main_list)

found_pack = 0

if resource_pack_name_part_to_search.lower() in str(listdir(getcwd())).lower():
    for pth in listdir(getcwd()):
        if path.isdir(f"{getcwd()}/{pth}") or is_zipfile(f"{getcwd()}/{pth}"):
            if resource_pack_name_part_to_search.lower() in pth.lower():
                found_pack = 1
                
                resource_pack_path = f"{getcwd()}/{pth}"

                print(f"Parsing: {resource_pack_path}")
                
                commands_list = []
                costumes = {}
                
                x_start_cord = 0
                z_start_coord = space_betwean_costumes_rows + 0
                
                max_costume_lenth = 1
                
                for file in open_pack(resource_pack_path):
 
                    costume_optifine_name = get_costume_optifine_name(file)
                    items = get_costume_items(file)
            
                    if not items:
                        continue

                    
                    if costume_optifine_name not in costumes.keys():
                        costumes[costume_optifine_name] = []
                    
                    for item in items:
                        item = item.replace("minecraft:", "")
                        if item not in items_ids.keys():
                            print(f"Item place is not defined: {item}")
                            while True:
                                print(f"Choose a place for the item: left arm = 6, right arm = 5, boots = 4, leggings = 3, chest = 2, head = 1")
                                item_place = input(f"{item}'s place is: ")
                                
                                if "!" + item_place not in items_places:
                                    print(f"Place '{item_place}' is not found! Try again!")
                                else:
                                    print()
                                    items_ids[item] = "!" + item_place
                                    break

                        if item not in costumes[costume_optifine_name]:
                            costumes[costume_optifine_name].append(item)


                for costume_name in costumes.keys():
                    costumes[costume_name], costume_lenth = sort_costume_armor(costumes[costume_name])
                    
                    if costume_lenth > max_costume_lenth:
                        max_costume_lenth = costume_lenth
                    
                    
                column_width = max_costume_lenth + ((max_costume_lenth-1) * space_betwean_armor_stands_in_rows) + space_betwean_costumes_columns

                print(f"Costumes: {len(costumes.keys())}")
                
                for costume_name in costumes.keys():
                    x_cord = x_start_cord + 0
                    z_coord = z_start_coord + 0

                    costume_items = costumes[costume_name]

                    for items in costume_items:
                        command = raw_command + ""
                        for item in items:
                            
                            item_propeties = semi_command.replace("ITEM", item).replace("OPTIFINE_NAME", costume_name)
                            
                            command = command.replace(items_ids[item], item_propeties)
                                
                        for place in items_places:
                            command = command.replace(place, "")
                            
                        commands_list.append(command.replace("XXX", str(x_cord)).replace("ZZZ", str(-z_coord)))
                        x_cord += space_betwean_armor_stands_in_rows + 1
                        
                        
                    z_start_coord += space_betwean_costumes_rows
                    
                    if (z_start_coord / space_betwean_costumes_rows) / rows > 1:
                        x_start_cord += column_width
                        z_start_coord = space_betwean_costumes_rows + 0
                    
                    
                with open(f"{resource_pack_path}.txt", mode="w") as file:
                    file.write("\n".join(commands_list))
                
                write(path_to_ids, items_ids)

if found_pack == 0:
    print(f"Did not found any folder with '{resource_pack_name_part_to_search}' in its name!")


while True:
    pass  
