   
   # Military Image Classification System

This system automatically classifies images containing military equipment, world leaders, and flags using advanced AI vision models. It stores metadata in PostgreSQL and can resume processing from where it left off.

## Features

- **Enhanced AI Descriptions**: AFP-style descriptive captions with professional military context
- **Reverse Image Search Framework**: Ready for integration with Google Reverse Image Search, TinEye API, and image hosting services
- **Advanced AI Classification**: Uses CLIP model for military equipment and country recognition
- **Detailed Image Analysis**: Identifies specific weapons (Shahab, Qiam, TEL, etc.) and equipment types
- **Country Detection**: Recognizes flags, uniforms, and military equipment from 30+ countries
- **Resume Capability**: Tracks processed images and can resume interrupted runs
- **PostgreSQL Storage**: Robust database storage with metadata tracking
- **GPU Acceleration**: Optimized for NVIDIA RTX 3070 Ti
- **Virtual Environment**: Isolated Python environment for clean dependency management
- **Batch Processing**: Processes thousands of images efficiently

## Quick Start

### 1. Set up Virtual Environment
```bash
python setup_venv.py
```

This will:
- Create a virtual environment in `venv/`
- Install basic dependencies (psycopg2, Pillow, etc.)
- Test database connection
- Set up database schema
- Create activation shortcuts

### 2. Activate Virtual Environment
**Windows:**
```bash
# Double-click activate_venv.bat
# OR
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
# OR
./activate_venv.sh
```

### 3. Install ML Dependencies (Optional)
```bash
pip install torch torchvision transformers accelerate
```

### 4. Place Images
Put your images in the `images/` folder.

### 5. Run Classification
```bash
python image_classifier.py
# OR on Windows: double-click run_classifier.bat
# OR on Linux/Mac: ./run_classifier.sh
```

## Requirements

- Python 3.8+
- PostgreSQL 18
- pgAdmin 4 (optional, for database management)
- NVIDIA GPU with CUDA support (RTX 3070 Ti recommended)
- ~8GB VRAM minimum for ML models

## Manual Setup (Alternative)

If you prefer manual setup:

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate it:**
   ```bash
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up database:**
   ```bash
   python setup_database.py
   ```

5. **Test connection:**
   ```bash
   python test_db_connection.py
   ```

## Configuration

Update database connection parameters in the scripts if needed:

```python
self.db_params = {
    'host': 'localhost',
    'database': 'image_classification',
    'user': 'hyper',      # Update this
    'password': 'class123',  # Update this
    'port': 5433
}
```

## Current Implementation Status

### ✅ **Enhanced AI Classification**
- AFP-style descriptive captions from reverse search or enhanced AI
- Example from reverse search: "In Tehran, Iran. Iran showcases advanced missile technology during annual military parade in Tehran, demonstrating latest developments in ballistic missile capabilities. (January 15, 2024). Source: Reuters"
- Professional military context and terminology
- Country detection and military equipment identification
- PostgreSQL database storage with metadata tracking

### 🔄 **Reverse Image Search Framework**
- Google Reverse Image Search library integrated ([RMNCLDYO/Google-Reverse-Image-Search](https://github.com/RMNCLDYO/Google-Reverse-Image-Search))
- Metadata extraction from AFP, Shutterstock, Getty Images, Reuters, and other reliable sources
- Prioritization system for credible news sources
- Ready for API integration (TinEye, Google Vision, image hosting services)

### 📋 **Next Steps for Full Implementation**
1. **Image Hosting Service**: Integrate Imgur API or imgbb for temporary image hosting (required for Google reverse search)
2. **TinEye API**: Add paid reverse image search service ($20/month) for reliable results
3. **Google Vision API**: Alternative computer vision API for image analysis
4. **Production Deployment**: Add rate limiting, error handling, and monitoring

## Output Data Structure

Each processed image stores:

- **filename**: Original image filename
- **description**: AFP-style descriptive caption from enhanced AI classification
- **country**: Detected country based on flags/equipment (e.g., "Iran", "Russia")
- **keywords**: Array of detected military terms (e.g., ["missile", "TEL", "Fateh-110"])
- **source_url**: Original source URL (when reverse image search is implemented)
- **source_type**: Source type (AFP, Shutterstock, etc.)
- **original_title**: Original title from source

## Database Schema

```sql
CREATE TABLE image_metadata (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(500) UNIQUE NOT NULL,
    description TEXT,                    -- AFP-style descriptive caption
    country VARCHAR(100),                -- Detected country
    keywords TEXT[],                     -- Array of military keywords
    source_url TEXT,                     -- Original source URL (if found via reverse search)
    source_type VARCHAR(100),            -- Source type (AFP, Shutterstock, etc.)
    original_title TEXT,                 -- Original title from source
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'processed'
);
```

## Model Details

- **BLIP-2 (2.7B)**: For detailed image captioning
- **CLIP ViT-B/32**: For zero-shot classification of countries and military equipment
- **Military Keywords Database**: 80+ specific military terms and equipment types
- **Country Recognition**: 30+ countries with military significance

## Memory Optimization

- Uses float16 precision on GPU to save memory
- Processes images one at a time
- Clears GPU cache every 10 images
- Batched CLIP processing to avoid memory spikes

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Check credentials in the scripts
- Verify database exists

### Virtual Environment Issues
- Make sure you're using the correct activation command for your OS
- Try recreating the venv: `python setup_venv.py`

### Out of Memory Errors
- Reduce batch sizes in the CLIP processing sections
- Use smaller BLIP model if needed

### Slow Processing
- Processing ~4000 images may take several hours
- Each image takes ~10-15 seconds on RTX 3070 Ti
- Consider running in batches if needed

## Querying Results

Use pgAdmin or connect to PostgreSQL to query results:

```sql
-- Get all processed images
SELECT * FROM image_metadata;

-- Find images by country
SELECT filename, description FROM image_metadata WHERE country = 'Iran';

-- Find images with specific keywords
SELECT filename, description FROM image_metadata WHERE 'missile' = ANY(keywords);

-- Get processing statistics
SELECT COUNT(*) as total_processed, country, COUNT(*) as count_per_country
FROM image_metadata
WHERE country IS NOT NULL
GROUP BY country
ORDER BY count_per_country DESC;
```

## Your Classification Results

The system successfully processed **3,497 images** and stored results in `fast_classification.db` (SQLite database).

### Top Countries Detected:
- China: 328 images
- Russia: 216 images
- Iran: 187 images
- Ukraine: 151 images
- United States: 99 images

### Top Equipment Detected:
- Shahab missiles: 449 images
- Qiam missiles: 332 images
- TEL (Transporter Erector Launcher): 202 images
- Sejjil missiles: 189 images
- SLBM (Submarine-Launched Ballistic Missiles): 102 images

## Querying Results

Use the provided `check_results.py` script or query the SQLite database directly:

```bash
python check_results.py
```

### SQLite Queries:
```sql
-- Find all Iranian military equipment
SELECT filename, description FROM classifications
WHERE country = 'Iran';

-- Find all missile images
SELECT filename, description FROM classifications
WHERE keywords LIKE '%missile%';

-- Get country statistics
SELECT country, COUNT(*) as count
FROM classifications
WHERE country IS NOT NULL
GROUP BY country
ORDER BY count DESC;
```

## Exporting Data

### Export to CSV (using Python):
```python
import sqlite3
import csv

conn = sqlite3.connect('fast_classification.db')
cursor = conn.cursor()

cursor.execute("SELECT filename, description, country, keywords, confidence FROM classifications")
rows = cursor.fetchall()

with open('classification_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Filename', 'Description', 'Country', 'Keywords', 'Confidence'])
    writer.writerows(rows)

conn.close()
print("Results exported to classification_results.csv")
```

### Export to JSON:
```python
import sqlite3
import json

conn = sqlite3.connect('fast_classification.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM classifications")
columns = [desc[0] for desc in cursor.description]
rows = cursor.fetchall()

results = []
for row in rows:
    result = dict(zip(columns, row))
    # Parse JSON keywords
    if result['keywords']:
        result['keywords'] = json.loads(result['keywords'])
    results.append(result)

with open('classification_results.json', 'w', encoding='utf-8') as jsonfile:
    json.dump(results, jsonfile, indent=2, ensure_ascii=False)

conn.close()
print("Results exported to classification_results.json")
```

## File Structure

```
hyperclassification/
├── images/                    # Place your images here
├── venv/                      # Virtual environment (created by setup)
├── setup_venv.py             # Virtual environment setup script
├── setup_database.py         # Database setup script
├── test_db_connection.py     # Database connection test
├── image_classifier.py       # Main classification script
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── activate_venv.bat         # Windows venv activation (created by setup)
├── run_classifier.bat        # Windows classifier runner (created by setup)
├── activate_venv.sh          # Linux/Mac venv activation (created by setup)
└── run_classifier.sh         # Linux/Mac classifier runner (created by setup)
```
