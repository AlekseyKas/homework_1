import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data = json.load(open('bostv1.json'))

win_logs = []
dns_logs = []

for rec in data:
    result = rec.get('result', {})
    if result.get('sourcetype') == 'WinEventLog:Security':
        win_logs.append({
            'EventCode': result.get('EventCode'),
            'EventName': result.get('name', 'Unknown'),
            'ComputerName': result.get('ComputerName'),
            'user': result.get('user'),
            'New_Process_Name': result.get('New_Process_Name'),
            'Logon_ID': result.get('Logon_ID')
        })
    elif result.get('LogName') == 'DNS':
        dns_logs.append({
            'QueryName': result.get('Query Name'),
            'QueryType': result.get('Query Type'),
            'ClientIP': result.get('Client IP'),
            'ResponseCode': result.get('Response Code'),
            'ComputerName': result.get('ComputerName'),
            'body': result.get('body')
        })

df_win = pd.DataFrame(win_logs)
df_dns = pd.DataFrame(dns_logs)

print("=== WinEventLog Analysis ===")
print(df_win['EventCode'].value_counts())

print("\n=== DNS Analysis ===")
print(df_dns)

suspicious_win_events = {
    '4688': 'Process Creation',
    '4689': 'Process Exit',
    '4624': 'Successful Logon',
    '4703': 'Token Right Adjusted',
    '4656': 'Object Handle Requested'
}

suspicious_dns_domains = [
    'ajd92jd9d.com',
    'c2.maliciousdomain.com'
]

suspicious_events = []

for _, row in df_win.iterrows():
    code = str(row['EventCode'])
    name = row['EventName']
    comp = row['ComputerName']
    proc = row['New_Process_Name']
    
    if code == '4703':
        suspicious_events.append({
            'Type': 'WinEventLog',
            'Event': f"Token Rights Adjusted (Event {code})",
            'Details': f"Computer: {comp}",
            'Severity': 'High'
        })
    elif code == '4624':
        suspicious_events.append({
            'Type': 'WinEventLog',
            'Event': f"Successful Logon (Event {code})",
            'Details': f"User: {row.get('user')}, Computer: {comp}",
            'Severity': 'Medium'
        })
    elif code == '4656':
        suspicious_events.append({
            'Type': 'WinEventLog',
            'Event': f"Object Handle Requested (Event {code})",
            'Details': f"Computer: {comp}",
            'Severity': 'Medium'
        })

for _, row in df_dns.iterrows():
    body = str(row['body'])
    if 'for' in body:
        domain = body.split('for ')[1].split(' type')[0]
    else:
        domain = 'unknown'
    
    if 'malicious' in body or 'c2' in body:
        suspicious_events.append({
            'Type': 'DNS',
            'Event': f"Suspicious Domain: {domain}",
            'Details': f"Client IP: {row.get('ClientIP')}, Type: {row.get('QueryType')}",
            'Severity': 'Critical'
        })
    elif any(c.isalpha() and c.islower() for c in domain.replace('.', '')):
        suspicious_events.append({
            'Type': 'DNS',
            'Event': f"Random Domain: {domain}",
            'Details': f"Client IP: {row.get('ClientIP')}",
            'Severity': 'High'
        })

df_suspicious = pd.DataFrame(suspicious_events)

print("\n=== Suspicious Events ===")
print(df_suspicious)

top10 = df_suspicious['Event'].value_counts().head(10)

plt.figure(figsize=(12, 6))
sns.barplot(x=top10.values, y=top10.index, palette='Reds_r')
plt.xlabel('Count')
plt.ylabel('Suspicious Event')
plt.title('Top 10 Suspicious Events')
plt.tight_layout()
plt.savefig('suspicious_events.png', dpi=150)
print("\nChart saved to suspicious_events.png")

print("\n=== Top 10 Suspicious Events ===")
print(top10)
