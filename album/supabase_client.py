import os
from supabase import create_client

def get_client():
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"] 
    return create_client(url, key)