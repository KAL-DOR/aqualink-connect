 AquaHub - Predictive Water Resilience Platform
> **Spotting "Day Zero" risks 5-60 days before they happen**
AquaHub is a crowdsourced resilience platform that predicts water scarcity at the neighborhood level using hybrid sensing — combining satellite metrics with real-time social signals.
---
The Problem
Latin America faces chronic water scarcity affecting **9+ million residents** in Mexico City alone. Current systems are reactive: utilities only respond after complaints flood in. There's no early warning system to forecast drought conditions with sufficient lead time for proactive intervention.
**Key challenges:**
- 550+ neighborhoods simultaneously without water during peak crisis
- 54% of reported leaks never get fixed (19,173 reports in 2024)
- $1.38 trillion MXN annual cost of environmental degradation
- Water infrastructure losses due to delayed detection
---
The Solution
AquaHub crosses **hard data** with **soft signals** to create predictive intelligence:
 Hybrid Sensing Pipeline
- **Hard Sensors**: NASA POWER satellite metrics for soil moisture, OpenWeather precipitation & temperature data
- **Soft Sensors**: NLP sentiment analysis of Twitter/X reports to detect shortages in real-time
- **Context**: Population density, elevation, and cyclical temporal patterns
 Results
- **60-day rolling forecast** with 70-85% confidence (5-day horizon)
- **27 high-risk hotspots** identified for targeted intervention
- **16 boroughs** (alcaldías) monitored across Mexico City
- **<500ms** inference time per prediction
---
 Architecture
 flowchart TD
    A[Data Ingestion] --> B[Feature Engineering]
    B --> C[ML Models]
    C --> D[API Layer]
    D --> E[Frontend]
    
    subgraph DataSources[Data Sources]
        A1[OpenWeather API<br/>5-day forecast]
        A2[NASA POWER<br/>Soil moisture GWETPROF]
        A3[Twitter/X Scraping<br/>960+ social reports]
    end
    
    subgraph Features[14 Features]
        B1[Hard: precip, temp, soil]
        B2[Soft: sentiment, reports]
        B3[Context: population, elevation]
    end
    
    subgraph Models[ML Models]
        C1[XGBoost<br/>Risk 0-4 prediction]
        C2[DBSCAN<br/>27 hotspots]
    end
    
    subgraph API[FastAPI Endpoints]
        D1[/predict<br/>5-60 day forecast/]
        D2[/hotspots<br/>Risk zones/]
        D3[/alcaldias<br/>16 boroughs/]
    end
    
    A --> DataSources
    B --> Features
    C --> Models
    D --> API
    E[Interactive Map<br/>Color-coded risks<br/>60-day slider]
    
    style DataSources fill:#e1f5ff
    style Models fill:#e1ffe1
    style API fill:#fff5e1
---
## Features
### Predictive Engine
- **Temporal Forecasting**: 5-day (high confidence) to 60-day (trend analysis)
- **Geographic Coverage**: All 16 boroughs of Mexico City
- **Risk Classification**: CONAGUA standard (D0-D4) mapped to 0-4 indices
- **Confidence Scoring**: Probability distribution per prediction
### Hotspot Detection
- **DBSCAN Clustering**: Density-based spatial clustering
- **27 Priority Zones**: High-density complaint areas
- **Predictive Allocation**: Resource optimization for utilities
### Social Intelligence
- **Pain Keywords**: "sin agua", "tandeo", "fuga de agua", "no hay agua"
- **Sentiment Analysis**: TextBlob polarity scoring (-1 to +1)
- **Real-time Monitoring**: Continuous social signal ingestion
---
## Model Performance
| Metric | Value |
|--------|-------|
| Training Samples | 960 (May-Jul 2024) |
| Features | 14 (weather + social + context) |
| Classes | 5 (D0-D4 drought levels) |
| Top Feature | Soil Moisture (30.6%) |
| 2nd Feature | Month Cyclical (26%) |
| Inference Time | <500ms |
| API Latency | <10s for all 16 boroughs |
### Feature Importance
1. **soil_moisture_root** (30.6%) - Physical drought indicator
2. **month_sin** (16.1%) - Seasonal cyclical pattern
3. **temp_max_24h** (12.0%) - Heat stress correlation
4. **month_cos** (9.9%) - Seasonal complement
5. **sentiment_polarity** (9.4%) - Social validation
---
## Impact Metrics
### Population
- **17.7M residents** in Mexico City metropolitan area
- **9.1M+** directly covered by monitoring
- **550+ neighborhoods** with early warning capability
### Government Efficiency
- **40% reduction** in emergency response costs (estimated $400M-$1B MXN/year)
- **+46% leak detection** via automated sentiment analysis
- **15 days** → **5 days** forecast frequency (CONAGUA quincenal vs. AquaHub daily)
### Economic
- **$1,300-$2,299 MXN** saved per family in private water trucks during crisis
- **$1.38 trillion MXN** annual environmental degradation cost (addressable)
- **3x faster** response time vs. manual reporting systems
---
## Team
- **Development & ML**: Backend architecture, XGBoost modeling, API design
- **Data Engineering**: Pipeline construction, feature extraction, clustering
- **Frontend**: Interactive mapping, visualization, UX
- **Strategy**: Pivot decision, market analysis, pitch development
---
## Acknowledgments
- **START Mexico City** - Platform and mentorship
- **Google for Startups** - Partnership opportunity (in progress)
- **NASA POWER** - Satellite soil moisture metrics
- **OpenWeather** - Meteorological forecasting
---

## License
[MIT License](LICENSE)
---
*"We didn't take first place, but we built something that matters."*
