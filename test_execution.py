import time
import requests

BASE_URL = "http://localhost:8000/api/v2"

def main():
    # 1. Fetch available workflows
    print("Fetching workflows...")
    resp = requests.get(f"{BASE_URL}/studio/workflows")
    resp.raise_for_status()
    workflows = resp.json()
    
    if not workflows:
        print("No workflows found in the database. Ensure seed script has run.")
        return
        
    workflow = workflows[-1]
    workflow_id = workflow['id']
    expected_inputs = workflow.get('expected_inputs', {})
    
    print(f"Selected workflow: {workflow_id}")
    print(f"Expected inputs: {expected_inputs}")
    
    # 2. Prepare mock inputs for V2
    raw_inputs = {
        "history_text": "Käyttäjä: Miten suunnittelen hyvän muistipelin? Tekoäly: Suosittelen spatiaalista oppimista ja kertausta. Käyttäjä: Voiko siihen liittää pisteytyksen? Tekoäly: Kyllä, se lisää motivaatiota selvästi Blooms-taksonomian mukaisesti.",
        "product_text": "Opetusmateriaali: Muistipelin prototyyppi. Sisältää flashcard-ominaisuuden ja visuaaliset parit. Lisäksi mukana on ohjeet opettajalle ja oppilaille selkeästi dokumentoituna, jotta kokonaisuus toimii.",
        "reflection_text": "Peli tuntuu hieman liian yksinkertaiselta lukiolaisille, mutta voisi toimia ala-asteella. Jatkossa voisin pyrkiä lisäämään pelillistä haastetta ja monikerroksisempia oppimistavoitteita sitoutumisen parantamiseksi.",
        "guided_reflection": {
            "q1": "Mikä on oppimistavoite?",
            "a1": "Käsitteiden mieleenpalautus",
            "q2": "Miten sovellat teoriaa?",
            "a2": "Pelillistämisellä"
        }
    }
            
    # 3. Create Execution
    payload = {
        "workflow_id": workflow_id,
        "raw_inputs": raw_inputs
    }
    
    print("\nStarting execution with 4 distinct V1-ported input tracks...")
    create_resp = requests.post(f"{BASE_URL}/executions/", json=payload)
    if create_resp.status_code != 202:
        print(f"Failed to create execution: {create_resp.status_code} - {create_resp.text}")
        return
        
    execution = create_resp.json()
    execution_id = execution['id']
    print(f"Execution started! ID: {execution_id}")
    
    # 4. Poll for completion
    print("Polling for status...")
    while True:
        status_resp = requests.get(f"{BASE_URL}/executions/{execution_id}")
        if status_resp.status_code != 200:
            print(f"Error fetching status: {status_resp.status_code}")
            break
            
        current_state = status_resp.json()
        status = current_state.get('status')
        print(f"Current status: {status}")
        
        if status.upper() in ['COMPLETED', 'FAILED']:
            if status.upper() == 'FAILED':
                print(f"Execution failed: {current_state.get('error')}")
            else:
                print("Execution completed successfully!")
                print("\nResults Preview:")
                results = current_state.get('results', {})
                for step_id, step_result in results.items():
                    print(f"\n--- Step: {step_id} ---")
                    if isinstance(step_result, dict):
                        for k, v in step_result.items():
                            print(f"{k}: {v}")
                    else:
                        print(f"Result: {step_result}")
            break
            
        time.sleep(2)

if __name__ == "__main__":
    main()
