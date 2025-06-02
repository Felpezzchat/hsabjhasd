# backend/routes/photo_server_api.py
from flask import Blueprint, send_from_directory, current_app, abort
import os

photos_bp = Blueprint('photos_bp', __name__, url_prefix='/api/photos')

@photos_bp.route('/<path:filepath>')
def serve_client_photo(filepath):
    # filepath is expected to be like "<client_id>/<filename.ext>"
    # It's relative to the UPLOAD_FOLDER.
    
    upload_folder = os.path.abspath(current_app.config['UPLOAD_FOLDER'])
    # Safely join the upload_folder with the filepath.
    # os.path.normpath will resolve any ".." or "." components.
    requested_path_abs = os.path.normpath(os.path.join(upload_folder, filepath))

    current_app.logger.debug(f"Attempting to serve photo: original filepath='{filepath}', upload_folder='{upload_folder}', requested_path_abs='{requested_path_abs}'")

    # Security check: Ensure the resolved path is still within the UPLOAD_FOLDER.
    # This helps prevent path traversal attacks (e.g., if filepath is "../../etc/passwd").
    if not requested_path_abs.startswith(upload_folder + os.sep) and requested_path_abs != upload_folder : # os.sep for platform independence
        current_app.logger.warning(f"Path traversal attempt or invalid path: Resolved '{requested_path_abs}' is outside of upload folder '{upload_folder}'.")
        abort(404) # Not Found, or 403 Forbidden
            
    if not os.path.exists(requested_path_abs) or not os.path.isfile(requested_path_abs):
        current_app.logger.warning(f"Photo not found at path: {requested_path_abs}")
        abort(404)

    # send_from_directory requires the directory and the filename separately.
    # directory_name = os.path.dirname(requested_path_abs) # This would be absolute
    # filename = os.path.basename(requested_path_abs)
    # However, send_from_directory's first argument is relative to app root_path or blueprint static_folder.
    # For send_from_directory to work with an absolute path for the directory, it's more straightforward
    # to use the 'directory' argument of send_from_directory as the base UPLOAD_FOLDER,
    # and 'filepath' as the path relative to that directory.

    try:
        # current_app.logger.debug(f"Serving file '{filepath}' from directory '{upload_folder}'")
        return send_from_directory(upload_folder, filepath)
    except Exception as e:
        current_app.logger.error(f"Error serving photo '{filepath}' from '{upload_folder}': {e}")
        abort(500)
