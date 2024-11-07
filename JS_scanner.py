import requests
import re
import argparse
import json
import signal
import sys
import os
import colorama
from colorama import Fore, Style  # Import Fore and Style
from bs4 import BeautifulSoup
from pystyle import Center, Colors, Colorate, System, Write

colorama.init(autoreset=True)

logo = """
******************************************
░▀▀█░█▀▀░░░░░█▀▀░█▀▀░█▀█░█▀█░█▀█░█▀▀░█▀▄
░░░█░▀▀█░░░░░▀▀█░█░░░█▀█░█░█░█░█░█▀▀░█▀▄
░▀▀░░▀▀▀░▀▀▀░▀▀▀░▀▀▀░▀░▀░▀░▀░▀░▀░▀▀▀░▀░▀
 ➠ By : Ghost_sec (github.com/fa-rrel)  
 ➠ Telegram Group t.me/@ghostsec00      
 ➠ Youtube channel : ghost_sec            
******************************************             
"""

print(Colorate.Diagonal(Colors.purple_to_red, logo))

def extract_links_from_js(js_content):
    url_pattern = r'(https?://[^\s\'"<>]+)'
    return re.findall(url_pattern, js_content)

def extract_secrets(js_content):
    secret_patterns = {
    'google_api': r'AIza[0-9A-Za-z-_]{35}',
    'google_captcha': r'6L[0-9A-Za-z-_]{38}|^6[0-9a-zA-Z_-]{39}$',
    'google_oauth': r'ya29\.[0-9A-Za-z\-_]+',
    'amazon_aws_access_key_id': r'A[SK]IA[0-9A-Z]{16}',
    'amazon_mws_auth_token': r'amzn\.mws\.[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
    'amazon_aws_url': r'\b(?:s3\.amazonaws\.com|[a-zA-Z0-9_-]+\.s3\.amazonaws\.com)\b',
    'facebook_access_token': r'EAACEdEose0cBA[0-9A-Za-z]+',
    'authorization_basic': r'\bbasic\s+[a-zA-Z0-9=:_\+\/-]+\b',
    'authorization_bearer': r'\bbearer\s+[a-zA-Z0-9_\-\.=:_\+\/]+\b',
    'authorization_api': r'\bapi[key|\s*]+\s*[a-zA-Z0-9_\-]+\b',
    'mailgun_api_key': r'\bkey-[0-9a-zA-Z]{32}\b',
    'twilio_api_key': r'\bSK[0-9a-fA-F]{32}\b',
    'twilio_account_sid': r'\bAC[a-zA-Z0-9_\-]{32}\b',
    'twilio_app_sid': r'\bAP[a-zA-Z0-9_\-]{32}\b',
    'paypal_braintree_access_token': r'access_token\$production\$[0-9a-z]{16}\$[0-9a-f]{32}',
    'square_oauth_secret': r'\bsq0csp-[0-9A-Za-z\-_]{43}|sq0[a-z]{3}-[0-9A-Za-z\-_]{22,43}\b',
    'square_access_token': r'\bsqOatp-[0-9A-Za-z\-_]{22}|EAAA[a-zA-Z0-9]{60}\b',
    'stripe_standard_api': r'\bsk_live_[0-9a-zA-Z]{24}\b',
    'stripe_restricted_api': r'\brk_live_[0-9a-zA-Z]{24}\b',
    'github_access_token': r'(?<=://)[a-zA-Z0-9_-]*:[a-zA-Z0-9_\-]+@github\.com',
    'rsa_private_key': r'-----BEGIN RSA PRIVATE KEY-----[\s\S]+?-----END RSA PRIVATE KEY-----',
    'ssh_dsa_private_key': r'-----BEGIN DSA PRIVATE KEY-----[\s\S]+?-----END DSA PRIVATE KEY-----',
    'ssh_dc_private_key': r'-----BEGIN EC PRIVATE KEY-----[\s\S]+?-----END EC PRIVATE KEY-----',
    'pgp_private_block': r'-----BEGIN PGP PRIVATE KEY BLOCK-----[\s\S]+?-----END PGP PRIVATE KEY BLOCK-----',
    'json_web_token': r'\beyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*\b',
    'jira_token': r'ATATT3[a-zA-Z0-9_\-+=]{184,195}$',
    'azure_openai_api_key': r'[a-f0-9]{32}$',
    }

    found_secrets = {}
    for key, pattern in secret_patterns.items():
        matches = re.findall(pattern, js_content)
        if matches:
            unique_matches = list(set(matches))
            found_secrets[key] = unique_matches

    object_pattern = r'(?i)const\s+[A-Z_]+_KEYS\s*=\s*\{([^}]+)\}'
    object_matches = re.findall(object_pattern, js_content)
    
    for match in object_matches:
        for line in match.split(','):
            line = line.strip()
            for key in secret_patterns.keys():
                if key.lower().replace(' ', '_') in line.lower():
                    value = re.search(r'\:\s*[\'"]?([^\'", ]+)[\'"]?', line)
                    if value:
                        found_secrets[key] = found_secrets.get(key, []) + [value.group(1)]

    return found_secrets


def signal_handler(sig, frame):
    choice = input(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Do you want to close dude? (Y/N): ").strip().lower()
    if choice == 'y':
        print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} Closing byee...")
        sys.exit(0)
    else:
        print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} Continuing execution...")

def main(input_file, output_file, look_for_secrets, look_for_urls, single_url):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(logo)

    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

    js_links = []
    if single_url:
        js_links.append(single_url)
    else:
        with open(input_file, 'r') as file:
            js_links = file.readlines()

    extracted_links = []
    all_secrets = {}

    for js_link in js_links:
        js_link = js_link.strip()
        if not js_link:
            continue
        
        try:
            response = requests.get(js_link, verify=False)
            response.raise_for_status()

            if look_for_urls:
                links = extract_links_from_js(response.text)
                extracted_links.extend(links)
                print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {Fore.YELLOW}Extracted {len(links)} links from {js_link}{Style.RESET_ALL}")

                for link in links:
                    print(f"{Fore.GREEN}[+] {link}{Style.RESET_ALL}")
                if not links:
                    print(f"{Fore.RED}[INFO]{Style.RESET_ALL} {Fore.YELLOW}No URLs found in {js_link}{Style.RESET_ALL}")

            if look_for_secrets:
                secrets = extract_secrets(response.text)
                if secrets:
                    all_secrets[js_link] = secrets
                    print(f"{Fore.GREEN}[+] Secrets found in {js_link}: {json.dumps(secrets, indent=2)}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}[INFO]{Style.RESET_ALL} {Fore.YELLOW}No secrets found in {js_link}{Style.RESET_ALL}")

        except requests.exceptions.SSLError as ssl_err:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} SSL error while fetching {js_link}: {str(ssl_err)}")
        except requests.RequestException as e:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Failed to fetch {js_link}: {str(e)}")

    if extracted_links and look_for_urls:
        with open(output_file, 'w') as out_file:
            for link in extracted_links:
                out_file.write(link + '\n')
        print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {Fore.YELLOW}Links saved to {output_file}{Style.RESET_ALL}")

    if all_secrets and look_for_secrets:
        secrets_output_file = output_file.replace('.txt', '_secrets.json')
        with open(secrets_output_file, 'w') as secrets_file:
            json.dump(all_secrets, secrets_file, indent=2)
        print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {Fore.YELLOW}Secrets saved to {secrets_output_file}{Style.RESET_ALL}")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTSTP, signal_handler)

    parser = argparse.ArgumentParser(description='Extract links and secrets from JavaScript files.')
    parser.add_argument('input_file', nargs='?', help='File containing JavaScript links')
    parser.add_argument('-o', '--output_file', default='extracted_links.txt', help='File to save extracted links')
    parser.add_argument('-u', '--url', help='Single JavaScript URL to fetch')
    parser.add_argument('--secrets', action='store_true', help='Look for secrets in JavaScript content')
    parser.add_argument('--urls', action='store_true', help='Extract URLs from JavaScript content')
    args = parser.parse_args()

    if not args.input_file and not args.url:
        print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {Fore.YELLOW} Please provide either an input file or a single URL.{Style.RESET_ALL}")
        sys.exit(1)
    if args.url and args.input_file:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Please provide either an input file or a single URL, not both.")
        sys.exit(1)

    main(args.input_file, args.output_file, args.secrets, args.urls, args.url)
