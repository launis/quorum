import json

def restore_slugs():
    with open('backend/seed/seed_data copy.json', encoding='utf-8') as f:
        orig = json.load(f)

    slug_map_users = {}
    for u in orig.get('users', []):
        slug_map_users[u.get('email')] = u.get('uid')

    slug_map_orgs = {}
    for o in orig.get('organizations', []):
        slug_map_orgs[o.get('name')] = o.get('id')

    with open('backend/seed/seed_data.json', encoding='utf-8') as f:
        target = json.load(f)

    for o in target.get('organizations', []):
        if o.get('name') in slug_map_orgs:
            o['slug'] = slug_map_orgs[o.get('name')]
            print(f"Restored org slug: {o['name']} -> {o['slug']}")

    for u in target.get('users', []):
        if u.get('email') in slug_map_users:
            u['slug'] = slug_map_users[u.get('email')]
            print(f"Restored user slug: {u['email']} -> {u['slug']}")

    with open('backend/seed/seed_data.json', 'w', encoding='utf-8') as f:
        json.dump(target, f, ensure_ascii=False, indent=4)
        print('Saved seed_data.json')

if __name__ == '__main__':
    restore_slugs()
