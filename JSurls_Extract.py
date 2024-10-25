import requests
import re
import argparse
import sys
from colorama import Fore, Style, init

init(autoreset=True)

print(f"""{Fore.BLUE}{Style.BRIGHT}
     _ ____     _____      _                  _   
    | / ___|   | ____|_  _| |_ _ __ __ _  ___| |_ 
 _  | \___ \   |  _| \ \/ / __| '__/ _` |/ __| __|
| |_| |___) |  | |___ >  <| |_| | | (_| | (__| |_ 
 \___/|____/___|_____/_/\_\\__|_|  \__,_|\___|\__|
          |_____| By Ghost_Sec{Style.RESET_ALL}
""")

def scan_js_links(file_path, output_path=None):
    try:
        with open(file_path, 'r') as file:
            urls = [line.strip() for line in file]
    except FileNotFoundError:
        print(f"{Fore.RED}{Style.BRIGHT}[ERROR]{Style.RESET_ALL} File '{file_path}' not found.")
        sys.exit(1)

    js_links = {}
    output_file = open(output_path, 'w') if output_path else None

    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
            js_files = re.findall(r'https://[^"]*\.js', response.text)
            js_links[url] = js_files

            print(f"{Fore.GREEN}{Style.BRIGHT}[{url}]{Style.RESET_ALL} -> {Fore.YELLOW}Found {len(js_files)} JS links:")
            for js in js_files:
                print(f"{Fore.CYAN}{Style.BRIGHT}  - {js}")
            
            if output_file:
                output_file.write(f"[{url}] -> Found {len(js_files)} JS links:\n")
                for js in js_files:
                    output_file.write(f"  - {js}\n")
        except requests.RequestException:
            error_msg = f"{Fore.RED}{Style.BRIGHT}[ERROR]{Style.RESET_ALL} Couldn't reach {url}"
            print(error_msg)
            if output_file:
                output_file.write(f"[ERROR] Couldn't reach {url}\n")

    if output_file:
        output_file.close()

    return js_links

def main():
    parser = argparse.ArgumentParser(description="Mass JS Link Scanner")
    parser.add_argument("-f", "--file", required=True, help="Path to the file with list of URLs")
    parser.add_argument("-o", "--output", help="Path to the output file to save results")
    args = parser.parse_args()

    scan_js_links(args.file, args.output)

if __name__ == "__main__":
    main()
