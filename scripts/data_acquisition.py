import os
import logging
import requests

logger = logging.getLogger(__name__)

def download_dataset(url, output_path):
    logger.info(f"Downloading dataset from {url}")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        logger.info(f"Dataset downloaded successfully to {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error downloading dataset: {str(e)}")
        raise

def acquire_data(output_dir, dataset_url=None):
    os.makedirs(output_dir, exist_ok=True)
    
    if not dataset_url:
        raise ValueError("Dataset URL must be provided")
    
    file_ext = dataset_url.split('.')[-1].lower()
    output_path = os.path.join(output_dir, f"online_retail.{file_ext}")
    
    return download_dataset(dataset_url, output_path)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example usage
    from config import RAW_DATA_DIR, DATASET_URL
    acquire_data(RAW_DATA_DIR, dataset_url=DATASET_URL)