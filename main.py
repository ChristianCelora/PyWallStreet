import sys 
import os
import json
import request

def getAlphaVantageKey() -> str:
    script_dir = os.path.dirname(__file__) #absolute dir the script is in
    json_data = ""
    #read file
    with open(script_dir+"\\alpha_vantage_key.json", "r") as f:
        json_data = json.load(f)
    #get JSON data
    if not "key" in json_data:
        raise Exception("chiave AlphaVantage non trovata")
    #get key
    print(json_data)
    alpha_key = json_data["key"]
    return alpha_key

def main():
    alpha_key = getAlphaVantageKey()
    print("AlphaVantage key:", alpha_key)
    sys.exit(1)

if __name__ == "__main__":
    main()

