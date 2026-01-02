import logging
import time
import uuid
from typing import Optional, List, Dict, Any
from tinydb import Query

from backend.models.auth import User, UserCreate, UserUpdate, UserRole, TokenData, Organization, OrganizationCreate
from backend.database.wrapper import AbstractDatabase, AbstractTable

logger = logging.getLogger(__name__)

# --- Repository Layer (Organization) ---

class OrganizationRepository:
    def __init__(self, db_client: AbstractDatabase):
        self.table: AbstractTable = db_client.table("organizations")
        
    def get_by_id(self, org_id: str) -> Optional[Organization]:
        # TinyDB simulation for get
        result = self.table.get(lambda x: x.get('id') == org_id)
        if result: 
            # Robustness: existing data might miss 'tier'
            if 'tier' not in result: result['tier'] = 'standard'
            return Organization(**result)
        return None
        
    def create(self, org: Organization) -> Organization:
        self.table.insert(org.model_dump())
        return org
        
    def list_all(self) -> List[Organization]:
        results = []
        for o in self.table.all():
            if 'tier' not in o: o['tier'] = 'standard'
            results.append(Organization(**o))
        return results

# --- Repository Layer (User) ---

class UserRepository:
    """
    Handles persistence of User metadata (roles, display names, hierarchy)
    to the underlying database (TinyDB or Firestore).
    """
    def __init__(self, db_client: AbstractDatabase):
        self.table: AbstractTable = db_client.table("users")

    def get_by_uid(self, uid: str) -> Optional[User]:
        # TinyDB / Memory filter approach
        result = self.table.get(lambda x: x.get('uid') == uid)
        if result:
            return User(**result)
        return None
        
    def get_by_email(self, email: str) -> Optional[User]:
        result = self.table.get(lambda x: x.get('email') == email)
        if result:
            return User(**result)
        return None

    def create(self, user: User) -> User:
        data = user.model_dump()
        self.table.insert(data)
        return user

    def update(self, uid: str, updates: UserUpdate) -> Optional[User]:
        user = self.get_by_uid(uid)
        if not user:
            return None
            
        update_data = updates.model_dump(exclude_unset=True)
        if not update_data:
            return user

        # Update in DB
        self.table.update(update_data, lambda x: x.get('uid') == uid)
        
        # Return updated
        return self.get_by_uid(uid)

    def list_all(self) -> List[User]:
        raw_users = self.table.all()
        return [User(**u) for u in raw_users]

# --- Service Layer ---

class AuthService:
    """
    Hybrid Auth Service with Multi-Tenancy (SaaS).
    """
    def __init__(self, db_client: AbstractDatabase, use_firebase: bool = False):
        self.repo = UserRepository(db_client)
        self.org_repo = OrganizationRepository(db_client)
        self.use_firebase = use_firebase
        self._initialized_firebase = False
        
        if self.use_firebase:
            self._init_firebase()

    def _init_firebase(self):
        try:
            import firebase_admin
            from firebase_admin import auth
            self.firebase_auth = auth
            logger.info("[AuthService] Firebase Admin SDK initialized.")
            self._initialized_firebase = True
        except ImportError:
            logger.warning("[AuthService] Firebase SDK not installed. Falling back to Mock mode.")
            self.use_firebase = False

    def verify_token(self, token: str) -> TokenData:
        """
        Verifies a Bearer token.
        Returns TokenData (uid, role, organization_id).
        """
        # 1. Mock/Dev Mode check
        if not self.use_firebase or token.startswith("mock-token:"):
            # Expect format "mock-token:<uid>"
            if token.startswith("mock-token:"):
                uid = token.split(":")[1]
            else:
                uid = token 
            
            # Check if user exists in our DB
            user = self.repo.get_by_uid(uid)
            if not user:
                 raise ValueError(f"Mock User not found for UID: {uid}")
            
            return TokenData(uid=user.uid, role=user.role, email=user.email, organization_id=user.organization_id)

        # 2. Firebase Mode
        try:
            # Verify ID token
            decoded_token = self.firebase_auth.verify_id_token(token)
            uid = decoded_token['uid']
            email = decoded_token.get('email')
            
            # Sync/Get User from our DB
            user = self.repo.get_by_uid(uid)
            
            if not user:
                # Auto-registration for missing users found in Firebase
                logger.info(f"User {uid} not found in local DB. Auto-registering as MEMBER (No Org).")
                new_user = User(
                    uid=uid,
                    email=email if email else "unknown@example.com",
                    role=UserRole.MEMBER,
                    organization_id=None, # Orphan user
                    created_at=str(time.time())
                )
                self.repo.create(new_user)
                return TokenData(uid=uid, role=UserRole.MEMBER, email=email, organization_id=None)
            
            return TokenData(uid=user.uid, role=user.role, email=user.email, organization_id=user.organization_id)

        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise ValueError("Invalid credentials")

    def create_organization(self, creator_uid: str, org_create: OrganizationCreate) -> Organization:
        """
        Creates a new Tenant Organization and an initial Admin user for it.
        Only ROOT can do this.
        """
        creator = self.repo.get_by_uid(creator_uid)
        if not creator or creator.role != UserRole.ROOT:
            raise PermissionError("Only ROOT can create organizations.")
            
        # 1. Create Organization
        org_id = uuid.uuid4().hex[:8] # or derive from name
        new_org = Organization(
            id=org_id,
            name=org_create.name,
            created_at=str(time.time()),
            is_active=True
        )
        self.org_repo.create(new_org)
        
        # 2. Create the Org Admin
        admin_payload = UserCreate(
            email=org_create.admin_email,
            password=org_create.admin_password,
            display_name=org_create.admin_name,
            role=UserRole.ADMIN,
            organization_id=org_id
        )
        
        # Bypass hierarchy check since we are ROOT acting explicitly
        self._create_user_internal(creator.uid, admin_payload, force_org_id=org_id)
        
        return new_org

    def create_user(self, creator_uid: str, user_data: UserCreate) -> User:
        return self._create_user_internal(creator_uid, user_data)

    def _create_user_internal(self, creator_uid: str, user_data: UserCreate, force_org_id: str = None) -> User:
        creator = self.repo.get_by_uid(creator_uid)
        if not creator:
             raise ValueError("Creator not found")
             
        # Resolve Org ID
        target_org_id = force_org_id if force_org_id else creator.organization_id
        
        # If creator is ROOT, they can set any org ID (or none), but usually they use create_organization.
        # If creator is ADMIN, they MUST inherit org ID.
        if creator.role != UserRole.ROOT:
            if user_data.organization_id and user_data.organization_id != creator.organization_id:
                raise PermissionError("Cannot creating users in other organizations.")
            target_org_id = creator.organization_id
            
        # Enforce Role Hierarchy
        self._enforce_hierarchy(creator, user_data.role)

        new_uid = ""
        
        # 1. Create in Firebase (if enabled)
        if self.use_firebase and user_data.password:
            try:
                fb_user = self.firebase_auth.create_user(
                    email=user_data.email,
                    password=user_data.password,
                    display_name=user_data.display_name
                )
                new_uid = fb_user.uid
            except Exception as e:
                try:
                    existing = self.firebase_auth.get_user_by_email(user_data.email)
                    new_uid = existing.uid
                    logger.info(f"User {user_data.email} already in Firebase. Using existing UID.")
                except:
                     raise ValueError(f"Failed to create Firebase user: {e}")
        else:
            # Generate a mock UID
            new_uid = f"local_{uuid.uuid4().hex[:8]}"

        # 2. Create in Local DB
        new_user = User(
            uid=new_uid,
            email=user_data.email,
            display_name=user_data.display_name,
            role=user_data.role,
            organization_id=target_org_id, # Tenant ID
            created_at=str(time.time()),
            created_by=creator.uid
        )
        
        saved_user = self.repo.create(new_user)
        return saved_user

    def _enforce_hierarchy(self, creator: User, target_role: UserRole):
        # Root can do anything
        if creator.role == UserRole.ROOT:
            return

        # Org Admin can create: Admins (Co-Admins), Managers, Members, Viewers
        if creator.role == UserRole.ADMIN:
            if target_role == UserRole.ROOT:
                raise PermissionError("Admins cannot create Roots.")
            # Admin CAN create another ADMIN (new rule)
            return

        # Manager is now Technical Lead (Workflow Config), NOT User Manager.
        # So Manager cannot create users.
        if creator.role == UserRole.MANAGER:
             raise PermissionError("Managers are Technical Leads and cannot manage users. Ask an Admin.")
            
        raise PermissionError("This user role cannot create users")
            
        raise PermissionError("This user role cannot create users")

    def ensure_root_user(self, email: str = "root@example.com") -> User:
        """Bootstraps a root user and Development Scenario (Demo Corp) if needed."""
        
        # 0. Ensure SYSTEM Org exists (Container for Root)
        if not self.org_repo.get_by_id("system"):
            logger.info("[AuthService] Creating 'system' Organization.")
            self.org_repo.create(Organization(
                id="system",
                name="System Administration",
                created_at=str(time.time()),
                tier="enterprise"
            ))

        # 1. ROOT
        root = self.repo.get_by_uid("root_master")
        if not root:
            logger.warning(f"No Root user found. Creating bootstrap root: {email}")
            root = User(
                uid="root_master",
                email=email,
                role=UserRole.ROOT,
                organization_id="system",
                display_name="System Root",
                created_at=str(time.time())
            )
            self.repo.create(root)
        elif root.organization_id != "system":
            # Fix casing or drift if it was "SYSTEM" or None
            logger.info(f"Fixing root_master organization_id from '{root.organization_id}' to 'system'")
            self.repo.update("root_master", UserUpdate(organization_id="system"))
            root = self.repo.get_by_uid("root_master") # Refresh

            self.repo.update("root_master", UserUpdate(organization_id="system"))
            root = self.repo.get_by_uid("root_master") # Refresh

        return root

    # --- Dependency Injection Helpers (Static) ---
    @staticmethod
    def require_role(required_role: UserRole):
        """
        Returns a dependency that validates the user has the required role.
        Implicitly allows ROOT for everything.
        """
        from fastapi import Depends, HTTPException
        from backend.dependencies import get_current_user_from_header # Lazy import
        
        async def _role_checker(user: TokenData = Depends(get_current_user_from_header)):
            if user.role == UserRole.ROOT:
                return user
            
            if user.role != required_role:
                 raise HTTPException(status_code=403, detail=f"Insufficient privileges. Required: {required_role.value}")
            return user
            
        return _role_checker

    @staticmethod
    def get_current_user(
        from_header=None # Placeholder to match Depends signature if needed, but we delegate
    ):
        """
        Dependency alias for getting current user via header.
        Intended usage: user: TokenData = Depends(AuthService.get_current_user)
        """
        from fastapi import Depends
        from backend.dependencies import get_current_user_from_header
        
        # This one is tricky because Depends() needs a callable.
        # If we return a callable that Depends uses...
        return get_current_user_from_header
