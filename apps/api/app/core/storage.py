from supabase import create_client, Client
from app.core.config import settings

# Initialize Supabase client with Service Role Key (bypasses RLS for backend operations)
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

def get_presigned_upload_url(bucket_name: str, file_path: str) -> dict:
    """
    Generates a presigned URL and token for uploading a file directly to Supabase Storage.
    """
    response = supabase.storage.from_(bucket_name).create_signed_upload_url(file_path)
    
    # Handle SDK v2.x response format changes ('signed_url' instead of 'url')
    url = response.get("signed_url") or response.get("url")
    token = response.get("token")
    
    if not url:
        raise ValueError(f"Could not extract URL from Supabase response: {response}")
        
    return {
        "url": url,
        "token": token,
        "file_path": file_path
    }

def get_presigned_download_url(bucket_name: str, file_path: str, expires_in: int = 3600) -> str:
    """
    Generates a presigned URL for downloading/viewing a private file.
    """
    response = supabase.storage.from_(bucket_name).create_signed_url(file_path, expires_in)
    
    # In supabase-py v2.x, create_signed_url returns a list of dicts: [{"signedUrl": "..."}]
    if isinstance(response, list) and len(response) > 0:
        return response[0].get("signedUrl") or response[0].get("signed_url")
        
    # Fallback for older versions or different response structures
    return response.get("signedUrl") or response.get("signed_url") or response.get("url")