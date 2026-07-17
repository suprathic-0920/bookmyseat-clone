import os

files_to_fix = [
    os.path.join('templates', 'movies', 'event_payment_success.html'),
    os.path.join('templates', 'movies', 'event_list.html'),
    os.path.join('templates', 'movies', 'event_detail.html')
]

for filepath in files_to_fix:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace('${{', '₹{{')
        content = content.replace('Total Paid:</strong> $', 'Total Paid:</strong> ₹')
        content = content.replace('Price: $', 'Price: ₹')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

print("Currency signs fixed!")
