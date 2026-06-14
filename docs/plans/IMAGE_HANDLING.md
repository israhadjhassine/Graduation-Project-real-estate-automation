# Image Handling Documentation

This document explains the architecture, issues, and solutions related to image management in the Real Estate Automation platform.

## Architecture Overview

The image handling flow is as follows:

1.  **Frontend (Nuxt 4)**: Users select images in the `UploadModal.vue`.
2.  **API Layer**: The frontend sends a multi-part form request to the FastAPI backend at `/properties/{id}/images`.
3.  **Backend (FastAPI)**: 
    - The `properties` router receives the file list.
    - It calls the `storage` service for each file.
    - The `storage` service uploads the image to **ImageKit.io** using their Python SDK.
4.  **Database**: The backend stores the absolute URL returned by ImageKit in the `property_images` table.
5.  **Rendering**: The frontend uses a standardized composable to render these URLs properly, whether they are local or cloud-hosted.

---

## Issues & Solutions

### 1. Hardcoded Localhost Prefixes (Frontend)
**Issue**: The frontend was prepending `http://localhost:8000/` to all image paths. While this worked for local storage, it broke ImageKit URLs (e.g., `http://localhost:8000/https://ik.imagekit.io/...`).
**Solution**: Migrated all image rendering to the `useAssetUrl` composable. It uses the `getPublicUrl` utility which detects if a URL is already absolute and prevents double-prefixing.

### 2. Multi-Image Upload 404 (Backend)
**Issue**: The frontend attempted to upload all images at once to `/properties/{id}/images`, but the backend only implemented a single-image endpoint (`/upload-image`).
**Solution**: Implemented a new router endpoint `POST /properties/{id}/images` that accepts a `List[UploadFile]`, allowing batch uploads and consistent behavior with the frontend.

### 3. ImageKit SDK Type Error
**Issue**: The ImageKit Python SDK threw an `AttributeError: 'dict' object has no attribute '__dict__'` when passing upload options as a standard Python dictionary.
**Solution**: Switched to using `types.SimpleNamespace` to wrap the dictionary into an object, providing the `__dict__` interface required by the library's internal validation.

### 4. SDK Response Inconsistency
**Issue**: Different versions of the ImageKit SDK returned responses in varying formats (sometimes dictionaries, sometimes objects).
**Solution**: Hardened `backend/services/storage.py` to check for both object attributes and dictionary keys:
```python
if hasattr(result, 'url'):
    url = result.url
elif isinstance(result, dict):
    url = result.get('url')
```

---

## Best Practices

- **Adding new images**: Always use the `useAssetUrl` composable in Vue templates.
- **Environment Variables**: Ensure `IMAGEKIT_PUBLIC_KEY`, `IMAGEKIT_PRIVATE_KEY`, and `IMAGEKIT_URL_ENDPOINT` are set in `.env`.
- **Debugging**: ImageKit upload logs can be found in `upload_debug.log` inside the backend container.
