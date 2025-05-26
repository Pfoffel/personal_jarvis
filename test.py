import json

def load_file_content(path: str) -> str:
    """ loads the files content as a str given the path to it"""
    try:
        with open(path, "r" ) as f:
            return f.read()
    except Exception as e:
        return f"Error Occurred when reading file: {e}"
    
print(load_file_content("outputs/writing/reports/Weekly_Reflection_Report_2025-05-25.md"))
