
from backend.dependencies import get_db_client_dep
from backend.services.auth import AuthService

def check_state():
    print("--- DB STATE CHECK ---")
    db = get_db_client_dep()
    auth = AuthService(db, use_firebase=False)
    
    # Check Org
    sys_org = auth.org_repo.get_by_id("system")
    print(f"Org 'system': {sys_org}")
    
    sys_org_caps = auth.org_repo.get_by_id("SYSTEM")
    print(f"Org 'SYSTEM': {sys_org_caps}")
    
    # Check User
    root = auth.repo.get_by_uid("root_master")
    if root:
        print(f"User 'root_master' Org ID: '{root.organization_id}'")
    else:
        print("User 'root_master' NOT FOUND")

if __name__ == "__main__":
    check_state()
