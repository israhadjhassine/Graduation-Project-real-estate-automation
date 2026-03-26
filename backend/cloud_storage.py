import os
import base64
from datetime import datetime
from uuid import uuid4
from imagekitio import ImageKit

def log_debug(msg):
    with open("/app/upload_debug.log", "a") as f:
        f.write(f"{datetime.now()}: {msg}\n")
    print(msg, flush=True)

# Explicitly load from env
PUBLIC_KEY = os.environ.get("IMAGEKIT_PUBLIC_KEY")
PRIVATE_KEY = os.environ.get("IMAGEKIT_PRIVATE_KEY")
URL_ENDPOINT = os.environ.get("IMAGEKIT_URL_ENDPOINT")

log_debug(f"DEBUG: Initializing ImageKit with endpoint: {URL_ENDPOINT}")

if not all([PUBLIC_KEY, PRIVATE_KEY, URL_ENDPOINT]):
    log_debug("WARNING: Missing one or more ImageKit credentials!")

imagekit = None
try:
    imagekit = ImageKit(
        public_key=PUBLIC_KEY,
        private_key=PRIVATE_KEY,
        url_endpoint=URL_ENDPOINT
    )
    log_debug("✅ ImageKit SDK initialized successfully.")
except Exception as e:
    log_debug(f"❌ FAILED to initialize ImageKit: {e}")

async def upload_to_imagekit(file_obj, original_filename):
    if not imagekit:
        log_debug("❌ Upload failed: ImageKit not initialized.")
        return None
        
    try:
        log_debug(f"🚀 Starting upload for: {original_filename}")
        
        # Read content
        content = await file_obj.read()
        log_debug(f"📊 File read size: {len(content)} bytes")
        
        # Encode
        encoded = base64.b64encode(content).decode('utf-8')
        
        # Upload
        result = imagekit.upload_file(
            file=encoded,
            file_name=f"{uuid4()}_{original_filename}",
            options={
                "folder": "/properties/",
                "use_unique_file_name": True
            }
        )
        
        if result:
            log_debug(f"DEBUG: result type: {type(result)}")
            log_debug(f"DEBUG: result dir: {dir(result)}")
            
            # Try to find URL in common places
            url = getattr(result, 'url', None)
            if not url and hasattr(result, 'response_metadata'):
                log_debug(f"DEBUG: response_metadata: {result.response_metadata}")
            
            if url:
                log_debug(f"✅ ImageKit Upload Success: {url}")
                return url
            else:
                log_debug(f"❌ ImageKit Upload returned unexpected result: {result}")
                return None
            
    except Exception as e:
        import traceback
        log_debug(f"❌ CRITICAL error during ImageKit upload: {str(e)}")
        log_debug(traceback.format_exc())
        return None
