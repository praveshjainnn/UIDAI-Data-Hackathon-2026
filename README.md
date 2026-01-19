# 🏢 National MSME Analytics Portal

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Dash](https://img.shields.io/badge/Dash-2.0+-green.svg)](https://dash.plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive geospatial analytics dashboard for visualizing and analyzing Micro, Small, and Medium Enterprises (MSMEs) data across India. Built with Python Dash, this interactive portal provides data-driven insights into MSME distribution, social inclusion, employment patterns, and industry profiles.

## ✨ Features
### 🗺️ **Interactive Geospatial Visualization**
- Real-time India map with state-wise MSME density
- Bubble maps with dynamic sizing and color-coding
- Interactive tooltips and pan/zoom capabilities

### 📊 **Multi-Dimensional Analytics**

#### 1. **Location & Infrastructure Profile**
   - Total MSME count and distribution
   - District-wise enterprise density
   - DIC (District Industries Centre) mapping

#### 2. **Social Inclusion Analysis**
   - Gender-wise ownership distribution (Male/Female)
   - Social category breakdown (General/OBC/SC/ST)
   - Women entrepreneurship metrics
   - Inclusion insights and recommendations

#### 3. **Employment & Scale Metrics**
   - Total employment generation
   - Investment analysis (in Lakhs)
   - Enterprise type distribution (Micro/Small/Medium)
   - Employment efficiency ratios

#### 4. **Industry Profile**
   - Manufacturing vs Services distribution
   - NIC code-based sector mapping
   - Industry diversity index
   - Regional specialization patterns

#### 5. **MSME Development Score**
   - Composite scoring system (Scale, Social, Employment, Industry)
   - State-wise ranking and categorization
   - Multi-dimensional radar charts
   - Development category classification (Nascent/Emerging/Developing/Advanced)

### 🎯 **Decision Support System (DSS)**
- Strategic highlighting capabilities
- High MSME density zones identification
- Low female ownership area analysis
- High employment generator mapping
- Top districts ranking table

### 📤 **Data Upload Portal**
- Drag-and-drop CSV file upload
- Automatic data validation
- Real-time dashboard updates

## 🛠️ Tech Stack

- **Backend Framework**: Dash (Python web framework)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly, Plotly Express
- **UI Components**: Dash Bootstrap Components
- **Mapping**: OpenStreetMap integration
- **Server**: Flask (via Dash)

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/msme-analytics-portal.git
   cd msme-analytics-portal
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
    
   # On Windows
   venv\Scripts\activate

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare data files**
   
   Ensure the following CSV files are in the project directory:
   - `msme_merged.csv` - Master MSME dataset
   - `location_profile.csv` - Location and infrastructure data
   - `social_profile.csv` - Social inclusion metrics
   - `employment_profile.csv` - Employment and investment data
   - `industry_profile.csv` - Industry classification data
   - `composite_score.csv` - MSME development scores

5. **Add assets**
   
   Place the government emblem image in the `assets/` folder:
   - `assets/emblem.jpg` - National emblem

## 🚀 Usage

### Running the Dashboard

#### Method 1: Python Command
```bash
python app.py
```

#### Method 2: Using Batch File (Windows)
```bash
run_dashboard.bat
```

The dashboard will be accessible at: **http://127.0.0.1:8050**

### Using the Dashboard

1. **Main Dashboard View**
   - Use the **Profile View** dropdown to switch between different analytical views
   - Filter data by **State** and **District** using the dropdown selectors
   - Explore interactive maps and charts

2. **DSS Tools**
   - Click the **DSS Tools** button in the header
   - Select highlight options to identify strategic zones
   - View top districts ranking table
   - Read AI-generated decision insights

3. **Data Upload**
   - Click the **Data Upload** button
   - Drag and drop CSV files or click to browse
   - Verify upload success and reload dashboard

```

## 📊 Data Profiles

### Required CSV Columns

#### `msme_merged.csv`
- State, District, Dic_Name
- nic5digitcode (for industry classification)
- organisationtype
- enterprisetype

#### `location_profile.csv`
- State, District, Dic_Name
- msme_count

#### `social_profile.csv`
- State, District
- female_owned, male_owned, total_msmes
- sc_count, st_count, obc_count, general_count

#### `employment_profile.csv`
- State, District
- total_employment, total_investment, total_msmes
- enterprise_type_split, avg_employment

#### `industry_profile.csv`
- State, District
- manufacturing_pct, services_pct
- industry_diversity_index

#### `composite_score.csv`
- State
- Final_MSME_Score, Category
- Scale_Score, Social_Score, Employment_Score, Industry_Score

### DSS Tools
- Strategic Highlighting Interface
- Top Districts Ranking


## 👥 Authors

- **PRAVESH** - *Initial Development*

**Built with ❤️ for India's MSME Ecosystem**

### Common Issues

1. **Port Already in Use**
   ```bash
   # Change port in app.py (line 1038)
   app.run(debug=True, port=8051)
   ```

2. **Module Not Found Error**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **Data File Not Found**
   - Ensure all CSV files are in the correct directory
   - Check file paths in `app.py` (line 16)

4. **Map Not Displaying**
   - Check internet connection (requires OpenStreetMap)
   - Verify state coordinates in STATE_COORDS dictionary


## 📈 Future Enhancements

- [ ] Real-time data updates via API integration
- [ ] Export functionality (PDF/Excel reports)
- [ ] Advanced filtering and search capabilities
- [ ] Machine learning predictions for MSME growth
- [ ] Mobile-responsive design improvements
- [ ] Multi-language support (Hindi, regional languages)
- [ ] User authentication and role-based access
- [ ] Comparison tools for multiple states/districts

---

