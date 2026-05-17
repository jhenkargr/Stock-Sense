import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def get_supabase_client():
    """
    Creates and returns a Supabase client using environment variables.
    Returns None if credentials are not found.
    """
    url = os.environ.get("PROJECT_URL", "").replace("/rest/v1/", "").strip("/")
    key = os.environ.get("PUBLIC_URL")
    
    if not url or not key:
        return None
        
    try:
        return create_client(url, key)
    except Exception as e:
        print(f"Error initializing Supabase client: {e}")
        return None
