import json

with open(r'c:\src\quorum\backend_v2\seed\seed_data.json', 'r', encoding='utf-8') as f:
    seed = json.load(f)

new_profile = {
  'id': 'prf_f05ae1cfbed3',
  'slug': 'basic_report_3d_1d',
  'workflow_id': 'wf_d653170e174847559e08af42b938d826',
  'name': {
    'default_locale': 'fi',
    'translations': {
      'en': 'Basic Report (3D & 2D)',
      'fi': 'Perusraportti (3D & 2D)'
    }
  },
  'description': {
    'default_locale': 'fi',
    'translations': {
      'en': 'Strong argumentation (X) without cognitive depth (Y) remains hollow rhetoric. High cognitive depth (Y) is necessary to evaluate the text within the framework of slow, critical judgment (Z). All three define genuine intellectual robustness.',
      'fi': 'Vahva argumentointi (X) ilman kognitiivista syvyytt\u00e4 (Y) j\u00e4\u00e4 ontoksi retoriikaksi. Korkea kognitiivinen syvyys (Y) taas on v\u00e4ltt\u00e4m\u00e4t\u00f6n, jotta sit\u00e4 voidaan arvioida hitaan ja kriittisen harkinnan (Z) kehyksess\u00e4. Kaikki kolme m\u00e4\u00e4ritt\u00e4v\u00e4t aidon \u00e4lykkyyden.'
    }
  },
  'layouts': [
    {
      'layout_type': 'radar_3d',
      'title': {
        'default_locale': 'fi',
        'translations': {
          'en': 'Cognitive Intelligence (3D)',
          'fi': 'Kognitiivinen \u00c4ly (3D)'
        }
      },
      'description': {
        'default_locale': 'fi',
        "translations": {
          "en": "Strong argumentation (X) without cognitive depth (Y) remains hollow rhetoric. High cognitive depth (Y) is necessary to evaluate the text within the framework of slow, critical judgment (Z). All three define genuine intellectual robustness.",
          "fi": "Vahva argumentointi (X) ilman kognitiivista syvyytt\u00e4 (Y) j\u00e4\u00e4 ontoksi retoriikaksi. Korkea kognitiivinen syvyys (Y) taas on v\u00e4ltt\u00e4m\u00e4t\u00f6n, jotta sit\u00e4 voidaan arvioida hitaan ja kriittisen harkinnan (Z) kehyksess\u00e4. Kaikki kolme m\u00e4\u00e4ritt\u00e4v\u00e4t aidon \u00e4lykkyyden."
        }
      },
      'components': [
        'blk_371c7724eeba40218409b5a3697ac1d3',
        'blk_a0405e121dbf44bfa8ee80566f8d0c2a',
        'blk_9adcb55b7ba44baeaf8921cb2fb935dc'
      ],
      'show_text': True
    },
    {
      'layout_type': 'matrix_2d',
      'title': {
        'default_locale': 'fi',
        'translations': {
          'en': 'Governance Risk (2D)',
          'fi': 'Hallinnollinen Riski (2D)'
        }
      },
      'description': {
        'default_locale': 'fi',
        'translations': {
          'en': 'Adherence to organizational rules (X) alongside the identification of hidden biases (Y). High rule adherence (X) can still obscure severe linguistic distortions (Y), increasing the actual implementation risk.',
          'fi': 'Organisaation s\u00e4\u00e4nt\u00f6jen noudattaminen (X) rinnakkain piilevien asenteiden tunnistamisen (Y) kanssa. Korkea s\u00e4\u00e4nt\u00f6jen noudattaminen (X) voi silti piilottaa taakseen vakavia kielellisi\u00e4 v\u00e4\u00e4ristymi\u00e4 (Y), jolloin todellinen implementaatioriski kasvaa.'
        }
      },
      'components': [
        'blk_d0e240184e0a40759d37138a250bd0aa',
        'blk_8b12be64227c4abd83e2f409b5c3ce28'
      ],
      'show_text': True
    }
  ]
}

# Add only if not already there
found = False
for i, p in enumerate(seed.get('output_profiles', [])):
    if p.get('id') == new_profile['id']:
        seed['output_profiles'][i] = new_profile
        found = True
        break
        
if not found:
    seed.setdefault('output_profiles', []).append(new_profile)

with open(r'c:\src\quorum\backend_v2\seed\seed_data.json', 'w', encoding='utf-8') as f:
    json.dump(seed, f, indent=4, ensure_ascii=False)
