import os
from lingustruct.core import LinguStruct

def main():
    lingu_struct = LinguStruct(template_dir=os.path.join(os.path.dirname(__file__), '..', 'lingustruct', 'templates'))
    
    # ユーザー入力でmaster.jsonを生成
    project_id = input("Enter Project ID: ")
    version = input("Enter Project Version: ")
    
    replacements_master = {
        "PROJECT_ID": project_id,
        "VERSION": version
    }
    
    lingu_struct.generate_master_json(replacements_master, output_path=os.path.join('..', 'master.json'))
    
    # ユーザー入力でoverview.jsonを生成
    meta_description = input("Enter description for 'meta' module: ")
    arch_description = input("Enter description for 'arch' module: ")
    dep_res_description = input("Enter description for 'dep_res' module: ")
    err_handling_description = input("Enter description for 'err_handling' module: ")
    prio_description = input("Enter description for 'prio' module: ")
    abbr_description = input("Enter description for 'abbr' module: ")
    map_description = input("Enter description for 'map' module: ")
    p_order_description = input("Enter description for 'p_order' module: ")
    version_description = input("Enter description for 'version' module: ")
    tech_description = input("Enter description for 'tech' module: ")
    
    replacements_overview = {
        "META_DESCRIPTION": meta_description,
        "ARCH_DESCRIPTION": arch_description,
        "DEP_RES_DESCRIPTION": dep_res_description,
        "ERR_HANDLING_DESCRIPTION": err_handling_description,
        "PRIO_DESCRIPTION": prio_description,
        "ABBR_DESCRIPTION": abbr_description,
        "MAP_DESCRIPTION": map_description,
        "P_ORDER_DESCRIPTION": p_order_description,
        "VERSION_DESCRIPTION": version_description,
        "TECH_DESCRIPTION": tech_description
    }
    
    lingu_struct.generate_overview_json(replacements_overview, output_path=os.path.join('..', 'overview.json'))
    
    print("Project files have been generated successfully.")

if __name__ == "__main__":
    main()
