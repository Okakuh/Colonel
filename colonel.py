from os import walk, getcwd, listdir, path
from json import load


def read(file1: str) -> dict:
    with open(file=f"{getcwd()}/{file1}", mode="r", encoding="utf-8") as f:
        return load(f)


# -------------------------------------------------------------------------------------------------------------
colonel_settings = read("colonel_settings/colonel_settings.json")


resource_pack_name_part_to_search = colonel_settings["resource_pack_name_part_to_search"]

raw_command = colonel_settings["raw_command"]
semi_command = colonel_settings["item"]

items_places = colonel_settings["items_places"]

armor_parts = colonel_settings["armor_parts"]
armor_order = colonel_settings["armor_order"]


# -------------------------------------------------------------------------------------------------------------
items_ids = read("/colonel_settings/items_ids.json")


# -------------------------------------------------------------------------------------------------------------
output_settings = read("colonel_settings/output_settings.json")

space_betwean_costumes_rows = output_settings["space_betwean_costume_rows"]
space_betwean_costumes_columns = output_settings["space_betwean_columns"]

space_betwean_armor_stands_in_rows = output_settings["space_betwean_armor_stands_in_rows"]

rows = output_settings["costumes_in_columns"]

# -------------------------------------------------------------------------------------------------------------



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

def sort_costume_armor(unsorted_items: list[str]) -> list[list[str]]:
    global max_costume_lenth
    temp_dict = {}
    not_armor = []
    temp_list = []
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
    
    temp_list = list(temp_dict.values())
    if len(not_armor) != 0:
        temp_list += not_armor
    
    for lst in temp_list:
        main_list.append([lst[i:i+2] for i in range(0, len(lst), 2)])
    
    
    if len(main_list) > max_costume_lenth:
        max_costume_lenth = len(main_list)
    
    return main_list


if resource_pack_name_part_to_search in str(listdir(getcwd())):
    for pth in listdir(getcwd()):
        if path.isdir(f"{getcwd()}/{pth}"):
            if resource_pack_name_part_to_search in pth:
                
                resource_pack_path = f"{getcwd()}/{pth}"

                commands_list = []
                costumes = {}
                
                x_start_cord = 0
                z_start_coord = space_betwean_costumes_rows + 0
                
                max_costume_lenth = 1
                
                for root, _, files in walk(resource_pack_path):
                    for file in files:
                        if ".properties" in file:

                            with open(f"{root}\\{file}") as file_properties:
                                file_properties = file_properties.read()
                                f = file_properties.split("\n")

                                
                            costume_optifine_name = get_costume_optifine_name(f)
                            items = get_costume_items(f)
                    
                            if not items:
                                continue
                                
                            if costume_optifine_name not in costumes.keys():
                                costumes[costume_optifine_name] = []
                            
                            for item in items:
                                if item not in items_ids.keys():
                                    print(f"Item place is not defined: {item}")
                                    while True:
                                        print(f"Choose a place for the item form this list: left arm = 6, right arm = 5, boots = 4, leggings = 3, chest = 2, head = 1")
                                        item_place = input(f"{item}'s place is: ")
                                        
                                        if "!" + item_place not in items_places:
                                            print(f"Place '{item_place}' is not found! Try again!")
                                        else:
                                            items_ids[item] = "!" + item_place
                                            break

                                if item not in costumes[costume_optifine_name]:
                                    costumes[costume_optifine_name].append(item)


                for costume_name in costumes.keys():
                    costumes[costume_name] = sort_costume_armor(costumes[costume_name])

                column_width = max_costume_lenth + ((max_costume_lenth-1) * space_betwean_armor_stands_in_rows) + space_betwean_costumes_columns


                for costume_name in costumes.keys():
                    x_cord = x_start_cord + 0
                    z_coord = z_start_coord + 0

                    costume_items = costumes[costume_name]

                    for items in costume_items:
                        for pair in items:
                            
                            command = raw_command + ""
                            
                            for item in pair:
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
                
