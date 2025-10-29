Image Classification System

This system automatically classifies images containing military equipment, world leaders, and flags using **Google Cloud Vision API** for superior accuracy. It stores metadata in PostgreSQL and can resume processing from where it left off.

**🚀 Enhanced with Google Vision API for professional AFP/Shutterstock-style photo descriptions!**

## Features

- **Professional Photo Descriptions**: AFP/Shutterstock-style captions for photolibrary use
- **Google Vision API Integration**: Superior accuracy using Google Cloud Vision AI (no GPU required)
- **Smart Hybrid Processing**: Preserves existing classifications while using Vision API for new images
- **Enhanced Keywords**: Searchable military equipment and country tags for easy discovery
- **Text Recognition**: Extracts equipment markings, serial numbers, and text from images
- **Military Equipment Detection**: Identifies 80+ specific weapons (Shahab, Qiam, TEL, tanks, aircraft, etc.)
- **Country Recognition**: Detects flags, uniforms, and equipment from 30+ countries
- **Resume Capability**: Tracks processed images and can resume interrupted runs
- **PostgreSQL Storage**: Robust database storage with comprehensive metadata
- **Batch Processing**: Processes thousands of images efficiently with API rate limiting
- **Cost Effective**: ~$5-10 for 1,000 new images

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

#### Original CLIP-Based Classification
```bash
python image_classifier.py
# OR on Windows: double-click run_classifier.bat
# OR on Linux/Mac: ./run_classifier.sh
```

#### New Google Vision API Classification (Recommended)
```bash
# Test Google Vision API setup
python test_google_vision.py

# Process new images with Google Vision API (preserves existing data)
python google_vision_classifier.py
```

## Google Vision API Integration

The system now includes a **Smart Hybrid Classifier** that uses Google Cloud Vision API for superior accuracy:

### **Key Benefits**
- **Professional Photo Descriptions**: AFP/Shutterstock-style captions for photolibrary use
- **Enhanced Keywords**: Searchable military equipment and country tags
- **Better Accuracy**: Google Vision AI outperforms CLIP for military equipment
- **No GPU Required**: Runs entirely on Google Cloud servers
- **Text Recognition**: Can read equipment markings, serial numbers, flags
- **Preserves Existing Work**: Only processes NEW images not in your database
- **Cost Effective**: ~$5-10 for 1,000 new images

### **Setup Requirements**

1. **Enable Google Cloud Vision API**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable "Cloud Vision API"
   - Create an API key

2. **Update Environment Variables**:
   ```bash
   cp .env.example .env
   # Edit .env file with your GOOGLE_CLOUD_API_KEY
   ```

3. **Test Integration**:
   ```bash
   python test_google_vision.py
   ```

### **Usage Modes**

#### **Automatic Processing** (Recommended)
```bash
python google_vision_classifier.py
# Choose option 1
# Processes only NEW images not in your database
# Preserves all existing classifications
```

#### **Manual Enhancement**
```bash
# Re-analyze specific existing images for better accuracy
python google_vision_classifier.py
# Choose option 3 to enhance existing images
```

#### **Search by Description**
```bash
# Search existing images by description, keywords, or metadata
python google_vision_classifier.py
# Choose option 5 and enter search terms like 'aircraft', 'building', 'military'
```

#### **Batch Processing**
The system processes images in batches of 10 with delays to respect API limits.

### **Search Functionality**
```bash
python google_vision_classifier.py
# Choose option 5 and enter search terms

# Example searches:
# - 'aircraft' → Find all aircraft-related images
# - 'building' → Find buildings and facilities
# - 'military' → Find military-related content
# - 'huawei' → Find Huawei corporate images
# - 'embassy' → Find embassy and diplomatic facilities
```

### **Sample Results**

**Before (Generic CLIP):**
```
Description: "Military equipment image featuring soldier, military uniform"
Keywords: ["soldier", "military uniform"]
```

**After (Google Vision API):**
```
Description: "Iran showcases missile capabilities during military demonstration"
Keywords: ["missile", "missile system", "ballistic missile", "iran", "iran military", "TEL"]
```

The new system creates professional, searchable photo descriptions suitable for AFP/Shutterstock-style photolibraries.

## Requirements

### For Original CLIP-Based Classification
- Python 3.8+
- PostgreSQL 18
- pgAdmin 4 (optional, for database management)
- NVIDIA GPU with CUDA support (RTX 3070 Ti recommended)
- ~8GB VRAM minimum for ML models

### For Google Vision API Classification
- Python 3.8+
- PostgreSQL 18 (already configured)
- Google Cloud Vision API enabled
- Google Cloud API key
- Internet connection for API calls
- **No GPU required!**

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

### ✅ **Google Vision API Integration (Primary System)**
- **Professional Photo Descriptions**: AFP/Shutterstock-style captions for photolibrary use
- **Example**: "Advanced missile system displayed during military technology exhibition"
- **Enhanced Keywords**: Searchable military equipment tags (`missile`, `tank`, `iran`, etc.)
- **Text Recognition**: Extracts equipment markings and serial numbers
- **Smart Processing**: Only processes NEW images, preserves existing classifications
- **Superior Accuracy**: Google Vision AI outperforms local models
- **Cost Effective**: ~$5-10 for 1,000 images, no GPU required

### ✅ **Database & Storage**
- **PostgreSQL Integration**: Robust storage with comprehensive metadata
- **Resume Capability**: Tracks processed images and can resume interrupted runs
- **Batch Processing**: Handles thousands of images with API rate limiting

### 🔄 **Legacy Systems (Available)**
- **CLIP-Based Classification**: Original fast_classifier.py for GPU-based processing
- **Reverse Image Search**: Framework ready for web-based image search integration

### 📋 **Optional Enhancements**
1. **Image Hosting Integration**: For enhanced reverse image search capabilities
2. **TinEye API**: Additional reverse image search service
3. **Production Monitoring**: Rate limiting, error handling, and monitoring dashboards

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

The system successfully processed **2,051 images** and stored results in PostgreSQL database (`image_classification` → `image_metadata` table).

### Current Processing Status:
- **Total Images Processed**: 2,051 (preserved from previous classifications)
- **Google Vision API Images**: 115 (processed today with enhanced descriptions)
- **Images Ready for Processing**: 1,446 (new images awaiting classification)

### Sample Enhanced Descriptions:
- **"Advanced missile system displayed during military technology exhibition"**
- **"Military personnel in military uniform conducting field operations"**
- **"Heavy armored vehicle tank demonstrates military ground capabilities"**

### Enhanced Keywords Generated:
- **Missile Systems**: `missile`, `missile system`, `ballistic missile`, `Shahab`, `Qiam`, `TEL`
- **Military Personnel**: `military personnel`, `soldier`, `armed forces`, `military uniform`
- **Equipment**: `tank`, `main battle tank`, `armored vehicle`, `fighter jet`, `warship`

## Querying Results

Use pgAdmin 4 or connect to PostgreSQL to query results:

```bash
# Connect to PostgreSQL
psql -h localhost -p 5433 -d image_classification -U postgres
```

### PostgreSQL Queries:
```sql
-- Find all Iranian military equipment
SELECT filename, description FROM image_metadata
WHERE country = 'Iran';

-- Find all missile images
SELECT filename, description FROM image_metadata
WHERE keywords::text LIKE '%missile%';

-- Get country statistics
SELECT country, COUNT(*) as count
FROM image_metadata
WHERE country IS NOT NULL
GROUP BY country
ORDER BY count DESC;

-- Find Google Vision API processed images
SELECT filename, description, processed_at
FROM image_metadata
WHERE source_type = 'Google Vision API'
ORDER BY processed_at DESC;

-- Search by keywords
SELECT filename, description FROM image_metadata
WHERE 'missile' = ANY(keywords);

-- Search by description text (like the new search feature)
SELECT filename, description, country, keywords
FROM image_metadata
WHERE LOWER(description) LIKE '%aircraft%'
   OR LOWER(country) LIKE '%iran%'
   OR 'aircraft' = ANY(keywords)
ORDER BY confidence DESC;
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

The project directory is organized as follows:

```
hyperclassification/
├── images/                    # Contains a large number of image files for classification
├── Countries/                 # Organized country-specific images
├── venv/                      # Virtual environment (created by setup)
├── setup_venv.py             # Virtual environment setup script
├── setup_database.py         # Database setup script
├── google_vision_classifier.py # Smart hybrid classifier (main system)
├── image_classifier.py       # Legacy CLIP-based classifier
├── fast_classification.db     # SQLite database for classification results
├── image_classification.db    # SQLite database for image metadata
├── image_metadata.db          # SQLite database for metadata storage
├── activate_venv.bat         # Windows virtual environment activation script
├── run_classifier.bat        # Windows classifier runner script
├── requirements.txt          # Python dependencies
├── README.md                 # This file
```

## Additional Notes

- **Countries Directory**: Contains subdirectories for specific countries, useful for organizing images by region.
- **Images Directory**: Includes a large collection of images (e.g., military equipment, flags) for processing.
- **Database Files**: The project uses SQLite databases (`fast_classification.db`, `image_classification.db`, `image_metadata.db`) to store classification results and metadata.
- **Batch Files**: Windows users can use `activate_venv.bat` to activate the virtual environment and `run_classifier.bat` to run the classifier.

## Legacy Batch Files

**Note**: `run_classifier.bat` is a legacy Windows batch file that runs the original CLIP-based classifier. For the enhanced Google Vision API system, use:

```bash
python google_vision_classifier.py
```
