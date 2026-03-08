import requests
import json

# VirusTotal API key
API_KEY = 'c1e615d704b240316d15d30a808ed46ce722f78fc11f5691848c0ecc809e88b6'

# Function to get file report from VirusTotal
def get_file_report(file_hash):
    url = f'https://www.virustotal.com/api/v3/files/{file_hash}'
    headers = {
        'x-apikey': API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': f'Error {response.status_code}: {response.text}'}

# Example usage: Get report for a known file hash (you can replace with your own)
# This is a hash for a test file, replace with actual hash if needed
file_hash = '44d88612fea8a8f36de82e1278abb02f'  # Example hash, replace as needed

report = get_file_report(file_hash)
print(json.dumps(report, indent=4))

# Save the JSON response to a file
with open('virustotal_report.json', 'w') as f:
    json.dump(report, f, indent=4)

print("JSON response saved to virustotal_report.json")

# To run this script:
# 1. Make sure requests library is installed: pip install requests
# 2. Set your API_KEY variable with your VirusTotal API key
# 3. Replace file_hash with the hash of the file you want to check
# 4. Run: python script_task_1.py