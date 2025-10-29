Military Image Classification System

This system automatically classifies images containing military equipment, personnel, installations, and flags using **Google Cloud Vision API** for superior accuracy. It generates professional AFP/Shutterstock-style photo descriptions, searchable keywords, and stores comprehensive metadata in PostgreSQL.

**🚀 Professional Photo Library System with Web Enhancement & Smart Re-analysis!**

## Features

- **🖼️ Professional Photo Descriptions**: AFP/Shutterstock-style captions using Google Vision AI
- **🔍 Smart Re-analysis**: Update only descriptions/keywords, preserve all other metadata
- **🌐 Web-Enhanced Analysis**: Scrapes alt-text and descriptions from matching web images
- **🏷️ Enhanced Keywords**: 200+ searchable military equipment, personnel, and location tags
- **📝 Text Recognition**: Extracts equipment markings, serial numbers, and contextual text
- **🎯 Military Intelligence**: Identifies 150+ specific weapons, vehicles, and equipment types
- **🇺🇳 Global Recognition**: Detects flags, uniforms, and insignia from 50+ countries/entities
- **⏯️ Resume Capability**: Tracks processed images with timestamps for monitoring in pgAdmin
- **🗄️ PostgreSQL Storage**: Robust database with comprehensive metadata schema
- **⚡ Batch Processing**: Handles thousands of images with intelligent rate limiting
- **💰 Cost Effective**: ~$5-10 for 1,000 images, no GPU required
- **🔄 Archive Management**: Clean codebase with test/debug files organized in archive/
- **🕵️ Reverse Image Search**: Framework for finding similar images across the web

## Quick Start

### 1. Set up Environment
```bash
# One-command setup: creates venv, installs deps, sets up database
python setup_venv.py
```

**What this does:**
- Creates virtual environment in `venv/`
- Installs all dependencies (Google Cloud, PostgreSQL, web scraping)
- Sets up PostgreSQL database schema
- Tests connections and creates activation scripts

### 2. Configure Google Vision API
```bash
# 1. Get API key from Google Cloud Console
# 2. Create .env file
cp .env.example .env
# Edit .env with your GOOGLE_CLOUD_API_KEY
```

### 3. Place Images
Put your images in the `images/` folder. The system supports:
- **PNG, JPG, JPEG, GIF, BMP, WebP** formats
- **Recursive folder scanning** (subdirectories supported)
- **Automatic organization** by country in `Countries/` folder

### 4. Process Images

#### Primary Workflow: Smart Re-analysis (Recommended)
```bash
# Test analyzer on sample images first
python reanalyze_all_images.py
# Choose test batch, then proceed with full analysis

# Full re-analysis of all images (updates only descriptions/keywords)
python reanalyze_all_images.py
```

#### Alternative: Individual Image Processing
```bash
# Analyze single image with full web enhancement
python -c "
from google_vision_analyzer import GoogleVisionAnalyzer
analyzer = GoogleVisionAnalyzer()
result = analyzer.analyze_image('path/to/image.jpg')
print(result)
"
```

## Core System Architecture

### **Primary Components**

#### **`google_vision_analyzer.py`** - AI Analysis Engine
- **Google Cloud Vision API integration** for comprehensive image analysis
- **Web-enhanced descriptions** using reverse image search and web scraping
- **Smart keyword generation** with 200+ military equipment mappings
- **Context-aware processing** for military, political, and technical scenes
- **Language filtering** to ensure English-only professional descriptions

#### **`reanalyze_all_images.py`** - Batch Processing Orchestrator
- **Smart re-analysis** that updates only descriptions/keywords, preserves all other data
- **Progress tracking** with timestamps for pgAdmin monitoring
- **Test batch capability** for quality assurance before full runs
- **Rate limiting** and error handling for reliable batch processing
- **Database integration** with PostgreSQL for metadata storage

#### **`web_scraper.py`** - Web Enhancement Module
- **Alt-text extraction** from matching web images
- **Description scraping** from image hosting sites
- **Context enhancement** for better photo library descriptions
- **Quality filtering** to reject generic or inappropriate content

#### **`reverse_image_search.py`** - Web Discovery Framework
- **Google Lens integration** for finding similar images online
- **Source attribution** tracking for copyright and licensing
- **Metadata enrichment** from web sources
- **Reverse search capabilities** for duplicate detection

### **Smart Re-analysis Workflow**

The system uses an intelligent **re-analysis approach** that preserves your existing work:

1. **Preserves All Existing Data**: Country classifications, source URLs, timestamps
2. **Updates Only Descriptions**: Replaces generic CLIP descriptions with professional Vision AI captions
3. **Enhances Keywords**: Adds searchable military equipment tags
4. **Web Enhancement**: Pulls contextual information from matching web images
5. **Quality Assurance**: Filters out generic descriptions, ensures English-only output

### **Setup Requirements**

#### 1. **Google Cloud Vision API**
```bash
# Enable API in Google Cloud Console
# Create service account and download key
# Set environment variable
export GOOGLE_CLOUD_API_KEY="your_api_key_here"
```

#### 2. **PostgreSQL Database**
```bash
# Install PostgreSQL 18+
# Configure connection (default: localhost:5433)
python setup_database.py
```

#### 3. **Python Environment**
```bash
python setup_venv.py  # Creates venv and installs all dependencies
```

### **Usage Modes**

#### **Smart Re-analysis** (Primary Workflow)
```bash
# Test on sample images first
python reanalyze_all_images.py
# Select test batch → verify quality → proceed with full analysis

# Full re-analysis (updates descriptions/keywords only)
python reanalyze_all_images.py
# Preserves: countries, sources, timestamps, other metadata
# Updates: descriptions, keywords, processed_at timestamp
```

#### **Individual Image Analysis**
```bash
python -c "
from google_vision_analyzer import GoogleVisionAnalyzer
analyzer = GoogleVisionAnalyzer()
result = analyzer.analyze_image('path/to/image.jpg')
print(f'Description: {result[\"description\"]}')
print(f'Keywords: {result[\"keywords\"]}')
"
```

#### **Batch Processing**
The system processes images in batches of 10 with delays to respect API limits.

### **Search & Query Capabilities**

#### **PostgreSQL Queries**
```sql
-- Find images by military equipment
SELECT filename, description FROM image_metadata
WHERE 'missile' = ANY(keywords) OR LOWER(description) LIKE '%missile%';

-- Find images by country
SELECT filename, description FROM image_metadata
WHERE country = 'Iran' OR country = 'Russia';

-- Search by description content
SELECT filename, description FROM image_metadata
WHERE LOWER(description) LIKE '%fighter jet%' OR LOWER(description) LIKE '%aircraft%';

-- Find recently processed images
SELECT filename, description, processed_at FROM image_metadata
WHERE processed_at > NOW() - INTERVAL '1 day'
ORDER BY processed_at DESC;

-- Get processing statistics
SELECT country, COUNT(*) as image_count
FROM image_metadata
WHERE country IS NOT NULL
GROUP BY country
ORDER BY image_count DESC;
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

## System Requirements

### **Primary System (Google Vision API)**
- **Python 3.8+**
- **PostgreSQL 18+** (localhost:5433 default)
- **Google Cloud Vision API** enabled with service account key
- **Internet connection** for API calls
- **No GPU required** - runs entirely on Google Cloud servers
- **pgAdmin 4** (recommended for database management)

### **Dependencies (Auto-installed by setup_venv.py)**
```txt
google-cloud-vision      # Google Vision API client
psycopg2-binary          # PostgreSQL adapter
requests                 # HTTP requests for web scraping
beautifulsoup4           # HTML parsing
Pillow                   # Image processing
python-dotenv           # Environment variable management
fake-useragent          # User agent rotation
```

### **Legacy System (CLIP-based - Archived)**
- NVIDIA GPU with CUDA support (RTX 3070 Ti recommended)
- ~8GB VRAM minimum for ML models
- torch, torchvision, transformers (auto-installed)

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

## Project Structure

```
hyperclassification/
├── 📁 Core System Files
│   ├── google_vision_analyzer.py    # 🧠 AI analysis engine (Google Vision API)
│   ├── reanalyze_all_images.py      # 🔄 Batch re-analysis orchestrator
│   ├── web_scraper.py              # 🕷️ Web enhancement & alt-text extraction
│   └── reverse_image_search.py     # 🔍 Web discovery & reverse search framework
│
├── 📁 Setup & Configuration
│   ├── setup_venv.py               # ⚙️ Virtual environment & dependency setup
│   ├── setup_database.py           # 🗄️ PostgreSQL database initialization
│   ├── requirements.txt            # 📦 Python dependencies
│   └── .env.example               # 🔑 Environment variables template
│
├── 📁 Data & Images
│   ├── images/                     # 🖼️ Main image collection (recursive scanning)
│   ├── Countries/                  # 🌍 Auto-organized country-specific images
│   └── *.db                        # 💾 SQLite/PostgreSQL database files
│
├── 📁 Archive (Test/Debug Files)
│   ├── archive/                    # 📂 43+ archived test/debug scripts
│   │   ├── test_*.py              # 🧪 Test scripts
│   │   ├── debug_*.py             # 🔧 Debug utilities
│   │   ├── check_*.py             # ✅ Validation scripts
│   │   └── update_*.py            # 🔄 Update utilities
│
├── 📁 Documentation
│   ├── README.md                   # 📖 This file
│   ├── USER_GUIDE.md              # 📋 Detailed user guide
│   └── git_setup.md               # 🐙 Git setup instructions
│
└── 📁 Environment
    ├── venv/                      # 🐍 Virtual environment (auto-created)
    └── query                      # ❓ Query file (miscellaneous)
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
