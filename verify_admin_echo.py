
import asyncio
from fastapi import FastAPI, HTTPException
from httpx import AsyncClient, ASGITransport
from backend.main import http_exception_handler
from backend.api.admin_router import router as admin_router
from backend.models.auth import UserCreate, UserUpdate, UserRole, UserAdminView
from backend.dependencies import CurrentUserDep, AuthServiceDep
import logging

# Setup Logger to verify capture
logging.basicConfig(level=logging.ERROR)

app = FastAPI()
app.include_router(admin_router)
app.exception_handler(HTTPException)(http_exception_handler)

# Mocks
async def override_auth_service():
    class MockAuthService:
        async def create_user(self, creator_uid, user_data):
            if user_data.email == "exists@test.com":
                 raise PermissionError("Quota exceeded")
            if user_data.email == "invalid@test.com":
                 raise ValueError("Bad email")
            return UserAdminView(uid="new", email=user_data.email, role=user_data.role, organization_id="org1")

        async def update_user(self, initiator_uid, target_uid, updates):
            if target_uid == "missing":
                 # Mock service behavior that raises ValueError on missing
                 raise ValueError("User not found")
            if target_uid == "protected":
                 raise RuntimeError("LAST_ADMIN_PROTECTION")
            return UserAdminView(uid=target_uid, email="test@test.com", role=UserRole.ADMIN, organization_id="org1")
            
        async def delete_user(self, initiator_uid, target_uid):
             if target_uid == "protected":
                 raise RuntimeError("LAST_ADMIN_PROTECTION")
             return True

    return MockAuthService()

async def override_current_user_root():
    class Dummy:
         uid = "root_uid"
         role = UserRole.ROOT
         organization_id = "org1"
    return Dummy()

from backend.dependencies import get_current_user_from_header, get_auth_service

app.dependency_overrides[get_auth_service] = override_auth_service
app.dependency_overrides[get_current_user_from_header] = override_current_user_root

async def main():
    print("Verifying Admin Router Internal Echo Protocol...")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        
        # Test 1: Create User -> PermissionError -> 403 PERMISSION_DENIED
        print("Test 1: Create User -> PermissionError")
        resp = await ac.post("/admin/users", json={"email": "exists@test.com", "role": "MEMBER", "name": "Test", "organization_id": "org1"})
        data = resp.json()
        print(f"Response: {data}")
        if resp.status_code != 403:
             with open("status_fail.txt", "w") as f:
                 f.write(f"Status: {resp.status_code}\nBody: {data}")
             raise RuntimeError(f"FAILED Test 1: Status {resp.status_code} != 403. Body: {data}")
        if data["error_code"] != "PERMISSION_DENIED":
             with open("status_fail.txt", "w") as f:
                 f.write(f"Code: {data['error_code']}\nBody: {data}")
             raise RuntimeError(f"FAILED Test 1: Code {data['error_code']} != PERMISSION_DENIED. Body: {data}")

        # Test 2: Create User -> ValueError -> 400 INVALID_USER_DATA
        print("Test 2: Create User -> ValueError")
        resp = await ac.post("/admin/users", json={"email": "invalid@test.com", "role": "MEMBER", "name": "Test", "organization_id": "org1"})
        data = resp.json()
        print(f"Response: {data}")
        if resp.status_code != 400:
             raise RuntimeError(f"FAILED Test 2: Status {resp.status_code} != 400. Body: {data}")
        if data["error_code"] != "INVALID_USER_DATA":
             raise RuntimeError(f"FAILED Test 2: Code {data['error_code']} != INVALID_USER_DATA")

        # Test 3: Update User -> Missing -> 404 USER_NOT_FOUND
        print("Test 3: Update User -> Missing")
        resp = await ac.patch("/admin/users/missing", json={"name": "New Name"})
        data = resp.json()
        print(f"Response: {data}")
        if resp.status_code != 404:
             raise RuntimeError(f"FAILED Test 3: Status {resp.status_code} != 404. Body: {data}")
        if data["error_code"] != "USER_NOT_FOUND":
             raise RuntimeError(f"FAILED Test 3: Code {data['error_code']} != USER_NOT_FOUND")

        # Test 4: Update User -> Protected -> 409 LAST_ADMIN_PROTECTION
        print("Test 4: Update User -> Protected")
        resp = await ac.patch("/admin/users/protected", json={"role": "MEMBER"})
        data = resp.json()
        print(f"Response: {data}")
        if resp.status_code != 409:
             raise RuntimeError(f"FAILED Test 4: Status {resp.status_code} != 409. Body: {data}")
        if data["error_code"] != "LAST_ADMIN_PROTECTION":
             raise RuntimeError(f"FAILED Test 4: Code {data['error_code']} != LAST_ADMIN_PROTECTION")
        
        # Test 5: Delete User -> Protected -> 409 LAST_ADMIN_PROTECTION
        print("Test 5: Delete User -> Protected")
        resp = await ac.delete("/admin/users/protected")
        data = resp.json()
        print(f"Response: {data}")
        if resp.status_code != 409:
             raise RuntimeError(f"FAILED Test 5: Status {resp.status_code} != 409. Body: {data}")
        if data["error_code"] != "LAST_ADMIN_PROTECTION":
             raise RuntimeError(f"FAILED Test 5: Code {data['error_code']} != LAST_ADMIN_PROTECTION")


    print("ADMIN ROUTER ECHO PROTOCOL VERIFIED")

if __name__ == "__main__":
    asyncio.run(main())
