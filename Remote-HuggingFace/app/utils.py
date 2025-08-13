import logging
from huggingface_hub import scan_cache_dir


def get_downloaded_models():
    try:
        cache_info = scan_cache_dir()
        model_names = [model.repo_id for model in cache_info.repos]
        return model_names
    except:
        logging.warning("Failed to scan cache directory!")
        return []
