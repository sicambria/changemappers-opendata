# Geographic Data Repository

This directory contains geographic data for the ChangeMappers OpenData project, following the GeoJSON specification (RFC 7946).

## Directory Structure

```
geo/
├── layers/           # Thematic geographic layers
│   ├── initiative_locations.geojson
│   ├── organization_networks.geojson
│   ├── bioregions.geojson
│   ├── transitions.geojson
│   ├── events.geojson
│   ├── impact_zones.geojson
│   ├── community_networks.geojson
│   └── resource_flows.geojson
├── boundaries/       # Reference boundaries
│   └── world.geojson
└── README.md        # This documentation
```

## Layer Descriptions

### initiative_locations.geojson
Point locations of sustainability and social change initiatives worldwide. Each feature represents a specific initiative with metadata about its category, status, and activity timeline.

**Geometry Types:** Point  
**Feature Count:** 15  
**Properties:** id, name, entity_type, entity_id, description, category, status, created_at, updated_at

### organization_networks.geojson
Locations of organizations and networks supporting social change. Includes network hubs, educational institutions, grassroots organizations, and movement support structures.

**Geometry Types:** Point  
**Feature Count:** 12  
**Properties:** id, name, entity_type, entity_id, description, org_type, founded, website, created_at, updated_at

### bioregions.geojson
Bioregional boundaries based on ecological and watershed delineations. Defines natural geographic units for place-based organizing and ecological stewardship.

**Geometry Types:** Polygon  
**Feature Count:** 6  
**Properties:** id, name, entity_type, entity_id, description, bioregion_type, area_sqkm, dominant_ecosystem, created_at, updated_at

### transitions.geojson
Geographic zones showing systemic transitions and transformations. Includes economic restructuring, agricultural transformation, energy transition, and urban transformation zones.

**Geometry Types:** Polygon  
**Feature Count:** 10  
**Properties:** id, name, entity_type, entity_id, description, transition_type, start_year, status, created_at, updated_at

### events.geojson
Locations of conferences, gatherings, and workshops related to social change. Includes both past and upcoming events.

**Geometry Types:** Point  
**Feature Count:** 10  
**Properties:** id, name, entity_type, entity_id, description, event_type, event_date, duration_days, organizer, created_at, updated_at

### impact_zones.geojson
Defined areas for measuring social and ecological impact outcomes. Used for tracking metrics across food security, energy transition, biodiversity, and community resilience.

**Geometry Types:** Polygon  
**Feature Count:** 8  
**Properties:** id, name, entity_type, entity_id, description, zone_type, area_sqkm, population_estimate, metrics[], created_at, updated_at

### community_networks.geojson
Local community network visualizations showing the geographic extent of organized community initiatives and their connections.

**Geometry Types:** Polygon  
**Feature Count:** 12  
**Properties:** id, name, entity_type, entity_id, description, network_type, member_count, focus_areas[], created_at, updated_at

### resource_flows.geojson
Resource and knowledge flow patterns between initiatives and communities. Shows connections for seed exchange, knowledge transfer, and solidarity networks.

**Geometry Types:** LineString, Polygon  
**Feature Count:** 10  
**Properties:** id, name, entity_type, entity_id, description, flow_type, flow_direction, volume_estimate, created_at, updated_at

## Data Standards

### Coordinate Reference System
All data uses WGS 84 (EPSG:4326), referenced as `urn:ogc:def:crs:OGC:1.3:CRS84` per RFC 7946.

### Coordinate Order
Coordinates follow [longitude, latitude] order (x, y) as specified in RFC 7946.

### Entity Identifiers
Each feature includes a UUID v4 `entity_id` for unique identification across systems.

### Timestamps
All timestamps use ISO 8601 format with timezone (e.g., `2026-04-08T13:24:51+02:00`).

### Licensing
All data is licensed under Creative Commons Attribution-ShareAlike 4.0 International (CC-BY-SA-4.0).

## Data Quality

### Geographic Accuracy
Coordinates represent actual locations based on:
- City center points for urban initiatives
- Known facility addresses where applicable
- Geographic centroids for regional features
- Simplified boundaries for larger zones

### Feature Properties
Each feature includes:
- `id`: Sequential integer for the layer
- `name`: Descriptive name of the entity
- `entity_type`: Classification (initiative, organization, bioregion, etc.)
- `entity_id`: UUID v4 for unique identification
- `description`: Brief description of the entity
- `created_at`: ISO 8601 timestamp of data creation
- `updated_at`: ISO 8601 timestamp of last update

## Usage

### Loading in GIS Software
All files are standard GeoJSON and can be loaded in:
- QGIS (drag and drop)
- ArcGIS (GeoJSON driver)
- Mapbox Studio
- Leaflet/MapLibre applications

### Programmatic Access
```javascript
// Example: Loading with fetch
const response = await fetch('geo/layers/initiative_locations.geojson');
const geojson = await response.json();
console.log(geojson.features.length); // 15
```

### Filtering by Properties
```javascript
// Filter initiatives by category
const foodInitiatives = geojson.features.filter(
  f => f.properties.category === 'food_security'
);
```

## Maintenance

### Adding New Features
1. Generate UUID v4 for `entity_id`
2. Add sequential `id` following existing numbers
3. Include all required properties
4. Use accurate coordinates for real locations
5. Update this README with new feature counts

### Updating Existing Features
1. Update `updated_at` timestamp
2. Maintain `created_at` for historical reference
3. Document changes in commit messages

## Sources

Data compiled from:
- Initiative websites and public directories
- OpenStreetMap for geographic references
- Natural Earth for boundary references
- Direct input from community organizations

## Contact

For data corrections or additions:
- Open an issue on the repository
- Contact via changemappers.org

---

*Last updated: 2026-04-08*
