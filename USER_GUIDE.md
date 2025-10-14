# Military Image Classification System - User Guide

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Quick Start](#quick-start)
3. [System Architecture](#system-architecture)
4. [Configuration](#configuration)
5. [Usage Guide](#usage-guide)
6. [Database Management](#database-management)
7. [Customization](#customization)
8. [Troubleshooting](#troubleshooting)
9. [API Reference](#api-reference)
10. [Development Guide](#development-guide)

## 🚀 System Overview

This Military Image Classification System uses **Google Cloud Vision API** to automatically classify military equipment, personnel, and installations in images. It generates professional AFP/Shutterstock-style photo descriptions and searchable keywords for photolibrary use.

### Key Features

- **Professional Photo Descriptions**: AFP/Shutterstock-style captions
- **Google Vision AI**: Superior accuracy without GPU requirements
- **Smart Processing**: Preserves existing work, only processes new images
- **Enhanced Keywords**: Searchable military equipment tags
- **Text Recognition**: Extracts markings and serial numbers
- **Batch Processing**: Handles thousands of images efficiently

## 🎯 Quick Start

### 1. Environment Setup

```bash
# Set up virtual environment
python setup_venv.py

# Activate environment (Windows)
activate_venv.bat

# Install dependencies
pip install -r requirements.txt
```

### 2. Google Cloud Vision API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable "Cloud Vision API"
3. Create an API key
4. Add to `.env` file:
   ```bash
   GOOGLE_CLOUD_API_KEY=your_api_key_here
   ```

### 3. Database Connection

The system connects to PostgreSQL at `localhost:5433` with database `image_classification` and table `image_metadata`.

### 4. Run Classification

```bash
# Test Google Vision API
python test_google_vision.py

# Process new images (preserves existing data)
python google_vision_classifier.py
```

## 🏗️ System Architecture

### Core Components

#### `google_vision_analyzer.py`
- **Purpose**: Google Cloud Vision API integration
- **Features**:
  - Label detection for military equipment
  - Object localization for precise positioning
  - Text detection for markings and serial numbers
  - Image properties analysis
- **Output**: Professional descriptions and searchable keywords

#### `google_vision_classifier.py`
- **Purpose**: Main classification engine with smart processing
- **Features**:
  - Database integration (PostgreSQL)
  - Resume capability (tracks processed images)
  - Batch processing with rate limiting
  - Multiple connection fallback methods

#### Database Schema (`image_metadata` table)
```sql
- id: SERIAL PRIMARY KEY
- filename: VARCHAR(500) UNIQUE
- description: TEXT (AFP-style caption)
- country: VARCHAR(100) (detected country)
- keywords: TEXT[] (searchable tags)
- source_type: VARCHAR(100) (Google Vision API)
- processed_at: TIMESTAMP
- metadata_is_ai: BOOLEAN
```

## ⚙️ Configuration

### Environment Variables (`.env`)

```bash
# Required
GOOGLE_CLOUD_API_KEY=your_google_vision_api_key_here

# Optional
DB_HOST=localhost
DB_NAME=image_classification
DB_USER=postgres
DB_PASSWORD=password
DB_PORT=5433
LOG_LEVEL=INFO
```

### Database Connection Parameters

The system tries multiple connection methods:
1. `user='hyper', password='class123'`
2. `user='postgres', password='password'`
3. `user='postgres', password=''`

## 📖 Usage Guide

### Basic Usage

#### 1. Process All New Images
```bash
python google_vision_classifier.py
# Choose option 1
```
- Processes only NEW images not in database
- Preserves existing classifications
- Uses Google Vision API for superior accuracy

#### 2. Process Specific Image
```bash
python google_vision_classifier.py
# Choose option 2, then enter filename
```

#### 3. Enhance Existing Image
```bash
python google_vision_classifier.py
# Choose option 3, then enter filename
```

#### 4. Show Database Statistics
```bash
python google_vision_classifier.py
# Choose option 4
```

### Advanced Usage

#### Batch Processing Parameters
- **Batch Size**: 10 images per batch
- **Delay**: 0.5 seconds between requests
- **Memory Management**: Clears cache every 50 images

#### API Rate Limiting
- Respects Google Vision API quotas
- Automatic retry on failures
- Configurable delays between requests

## 🗄️ Database Management

### PostgreSQL Setup

1. **Install PostgreSQL** (version 18 recommended)
2. **Configure connection** in `setup_database.py`
3. **Run setup script**:
   ```bash
   python setup_database.py
   ```

### Database Queries

#### Find Images by Country
```sql
SELECT filename, description FROM image_metadata
WHERE country = 'Iran';
```

#### Find Images by Equipment
```sql
SELECT filename, description FROM image_metadata
WHERE 'missile' = ANY(keywords);
```

#### Get Processing Statistics
```sql
SELECT source_type, COUNT(*) as count
FROM image_metadata
GROUP BY source_type;
```

#### Recent Google Vision API Results
```sql
SELECT filename, description, processed_at
FROM image_metadata
WHERE source_type = 'Google Vision API'
ORDER BY processed_at DESC;
```

### Data Export

#### Export to CSV
```python
import psycopg2
import csv

conn = psycopg2.connect(host='localhost', database='image_classification',
                       user='postgres', password='password', port=5433)
cursor = conn.cursor()

cursor.execute("SELECT filename, description, country, keywords FROM image_metadata")
rows = cursor.fetchall()

with open('classification_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Filename', 'Description', 'Country', 'Keywords'])
    writer.writerows(rows)

conn.close()
```

## 🔧 Customization

### Modifying Description Templates

Edit `google_vision_analyzer.py` in the `_generate_description()` method:

```python
def _generate_description(self, equipment, countries, text):
    if equipment and countries:
        if 'missile' in equipment:
            return f"{countries[0]} showcases {equipment[0]} capabilities during military demonstration"
        # Add custom templates for other equipment types
```

### Adding New Military Keywords

Update the `military_labels` dictionary:

```python
self.military_labels = {
    'new_weapon': ['new weapon name', 'alternative name'],
    # Add more equipment types
}
```

### Custom Country Detection

Modify the `country_indicators` dictionary:

```python
self.country_indicators = {
    'New Country': ['new flag', 'new country flag'],
}
```

### Adjusting Confidence Thresholds

```python
# In _extract_military_equipment()
if confidence > 0.8:  # Adjust threshold as needed
    # Process high-confidence detections
```

## 🚨 Troubleshooting

### Common Issues

#### Google Vision API Errors
```bash
# Check API key
python -c "import os; print(os.getenv('GOOGLE_CLOUD_API_KEY'))"

# Test API connection
python test_google_vision.py
```

#### Database Connection Issues
```bash
# Test database connection
python test_db_connection.py

# Check PostgreSQL is running
# Windows: Services → PostgreSQL
# Linux: sudo systemctl status postgresql
```

#### No New Images Processed
```bash
# Check what images exist vs database
python -c "
import os
import psycopg2

# Count images
images = []
for root, dirs, files in os.walk('images'):
    for file in files:
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            images.append(file)

print(f'Images in directory: {len(images)}')

# Check database
conn = psycopg2.connect(host='localhost', database='image_classification', user='postgres', password='password', port=5433)
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM image_metadata')
db_count = cursor.fetchone()[0]
print(f'Images in database: {db_count}')
"
```

#### Generic Descriptions Instead of Enhanced
- Check if Vision API is detecting specific military equipment
- Use `debug_vision.py` to see what labels are being detected
- Ensure images contain recognizable military equipment

### Performance Optimization

#### Memory Management
- System clears GPU cache every 50 images (when using CLIP models)
- Batch processing prevents memory spikes

#### API Rate Limiting
- 0.5 second delay between requests
- Respects Google Vision API quotas

## 📚 API Reference

### GoogleVisionAnalyzer Class

#### Methods

**`analyze_image(image_path: str) -> Dict`**
- Analyzes single image using Google Vision API
- Returns: filename, description, country, keywords, confidence

**`test_connection() -> bool`**
- Tests Google Vision API connectivity
- Returns: True if successful

### GoogleVisionClassifier Class

#### Methods

**`process_all_new_images(batch_size: int = 10) -> Dict`**
- Processes all new images not in database
- Returns: processing statistics

**`should_process_image(filename: str) -> bool`**
- Checks if image needs processing
- Returns: True if not in database

**`save_result(result: Dict) -> bool`**
- Saves classification result to PostgreSQL
- Returns: True if successful

## 🛠️ Development Guide

### Code Structure

```
hyperclassification/
├── Core Classification:
│   ├── google_vision_analyzer.py    # Vision API integration
│   ├── google_vision_classifier.py  # Main classifier
│   └── image_classifier.py          # Legacy CLIP classifier
├── Database:
│   ├── setup_database.py           # PostgreSQL setup
│   └── test_db_connection.py       # Connection testing
├── Testing:
│   ├── test_google_vision.py       # API integration test
│   ├── debug_vision.py            # Vision API debugging
│   └── final_test.py              # System integration test
└── Utilities:
    ├── check_databases.py         # Database inspection
    └── requirements.txt           # Dependencies
```

### Adding New Features

#### New Equipment Detection
1. Add to `military_labels` dictionary in `google_vision_analyzer.py`
2. Update description templates in `_generate_description()`
3. Add keyword mappings in `_generate_photolibrary_keywords()`

#### Custom Processing Logic
1. Extend `GoogleVisionClassifier` class
2. Override processing methods as needed
3. Update database schema if required

### Testing New Features

```bash
# Test API integration
python test_google_vision.py

# Debug Vision API results
python debug_vision.py

# Test complete system
python final_test.py
```

## 📋 File Descriptions

### Core Files

**`google_vision_analyzer.py`**
- Google Cloud Vision API integration
- Military equipment detection and mapping
- Professional description generation
- Photolibrary keyword creation

**`google_vision_classifier.py`**
- Main classification engine
- PostgreSQL database integration
- Smart processing (preserves existing data)
- Batch processing with rate limiting

**`test_google_vision.py`**
- Google Vision API connection testing
- Image analysis testing
- System integration verification

### Utility Files

**`run_classifier.bat`**
- Legacy Windows batch file
- Runs original CLIP-based classifier
- **Not used** for Google Vision API system

**`setup_venv.py`**
- Virtual environment creation
- Dependency installation
- Database setup and testing

**`requirements.txt`**
- Python dependencies
- Includes: torch, transformers, psycopg2, Pillow, etc.

## 🎯 Best Practices

### For Users
1. **Regular Processing**: Run classification regularly to process new images
2. **Database Backups**: Backup PostgreSQL database regularly
3. **API Monitoring**: Monitor Google Vision API usage and costs
4. **Image Organization**: Keep images organized in `images/` directory

### For Developers
1. **Code Documentation**: Document new features and changes
2. **Testing**: Test new features before deployment
3. **Error Handling**: Implement proper error handling and logging
4. **Performance**: Monitor processing speed and memory usage

## 📞 Support

### Getting Help

1. **Check Logs**: Review console output for error messages
2. **Test Scripts**: Use provided test scripts to diagnose issues
3. **Database Inspection**: Use pgAdmin to inspect database contents
4. **Documentation**: Refer to this guide and README.md

### Common Solutions

- **API Key Issues**: Verify `GOOGLE_CLOUD_API_KEY` in `.env` file
- **Database Issues**: Check PostgreSQL service status
- **Processing Issues**: Verify image file formats and paths
- **Performance Issues**: Monitor system resources during processing

---

*This documentation covers the Google Vision API-powered Military Image Classification System. For the legacy CLIP-based system, refer to the original README sections.*
