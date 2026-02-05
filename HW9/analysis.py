import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re

# Stage 1: Load data from JSON
print("=== Этап 1: Загрузка данных ===")
with open('events.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Stage 2: Data Analysis
print("\n=== Этап 2: Анализ данных ===")

# Create DataFrame from events
events_list = data['events']
df = pd.DataFrame(events_list)

# Display basic info about the dataset
print(f"Общее количество событий: {len(df)}")
print(f"\nПервые 5 событий:")
print(df.head())

# Extract event types from signatures (first word before space)
# Event types are prefixes like MALWARE-CNC, EXPLOIT, INDICATOR-COMPROMISE, etc.
def extract_event_type(signature):
    """Extract the main event type from signature"""
    match = re.match(r'^([A-Z\-]+)', signature)
    if match:
        return match.group(1)
    return "UNKNOWN"

df['event_type'] = df['signature'].apply(extract_event_type)

# Analyze distribution of event types
print(f"\n=== Распределение типов событий ===")
event_counts = df['event_type'].value_counts()
print(event_counts)
print(f"\nВсего различных типов событий: {len(event_counts)}")

# Additional statistics
print(f"\nПроцентное распределение:")
print(df['event_type'].value_counts(normalize=True) * 100)

# Stage 3: Data Visualization
print("\n=== Этап 3: Визуализация данных ===")

# Set the style for better-looking plots
sns.set_style("whitegrid")
plt.figure(figsize=(12, 6))

# Create bar plot of event type distribution
event_counts.plot(kind='bar', color='steelblue', edgecolor='black')
plt.title('Распределение типов событий информационной безопасности', fontsize=14, fontweight='bold')
plt.xlabel('Тип события', fontsize=12)
plt.ylabel('Количество событий', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('event_distribution.png', dpi=300, bbox_inches='tight')
print("График сохранён в файл: event_distribution.png")
plt.show()

# Additional visualization: Pie chart
plt.figure(figsize=(10, 8))
colors = sns.color_palette("husl", len(event_counts))
plt.pie(event_counts, labels=event_counts.index, autopct='%1.1f%%', 
        colors=colors, startangle=90)
plt.title('Процентное распределение типов событий', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('event_distribution_pie.png', dpi=300, bbox_inches='tight')
print("Круговая диаграмма сохранена в файл: event_distribution_pie.png")
plt.show()

print("\n=== Анализ завершён ===")
