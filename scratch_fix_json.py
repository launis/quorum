path = 'backend_v2/seed/seed_data.json'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the unescaped quote issue
# It currently has: role (e.g., "**Käyttäjän Rooli: Arkkitehti**").
# We want it to be: role (e.g., \\"**Käyttäjän Rooli: Arkkitehti**\\").
content = content.replace('role (e.g., "**Käyttäjän Rooli: Arkkitehti**").', 'role (e.g., \\"**Käyttäjän Rooli: Arkkitehti**\\").')
# The original file might have encoding artifacts like Kyttjn
content = content.replace('role (e.g., "**Kyttjn Rooli: Arkkitehti**").', 'role (e.g., \\"**Käyttäjän Rooli: Arkkitehti**\\").')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fix applied.")
