
from backend.database.wrapper import get_db_client, get_db_path
db = get_db_client()
components = db.table('components')
coach_config = components.base_query({'id': 'COACH_OUTPUT_CONFIG'})
# TinyDB wrapper returns list for base_query usually, or we can iterate
# Since base_query might not be exposed directly on the wrapper in the way I think, 
# I'll use simple search.
# Actually, let's just inspect the raw table content if needed, but wrapper has .get_component_by_id logic usually in repository.
# Let's use the repository if possible, or just raw access.
from tinydb import Query
User = Query()
# Access raw tinydb
res = db.db.table('components').search(User.id == 'COACH_OUTPUT_CONFIG')
print(res)
