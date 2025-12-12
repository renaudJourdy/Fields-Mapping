# Enum Definitions

**Status:** ✅ Validated  
**Source:** `docs/enums/README.md`, `docs/enums/response.json`

Fleeti API enumerations for categorical fields used throughout the system.

---

## Overview

This document provides an overview of enumeration definitions used in the Fleeti system. Enumerations are categorical fields that use numeric codes to represent specific values (e.g., asset types, vehicle types, status codes).

**Data Source**: `docs/enums/response.json`

**Total Enums**: 45 enumeration types

---

## Enum Structure

Each enum includes:
- **Numeric values**: Integer codes used in the backend
- **Names**: Programmatic enum names (e.g., `Vehicle`, `Operational`)
- **Localization**: French (`fr`) and English (`en`) translations
- **Images**: SVG icon URLs for visual representation (available for some enums)

### JSON Structure

```json
{
  "results": [
    {
      "enum": "EnumName",
      "values": [
        {
          "value": 10,
          "name": "EnumValue",
          "fr": "French Translation",
          "en": "English Translation",
          "image": "https://..." // Optional
        }
      ]
    }
  ],
  "resultsCounted": 45,
  "isSuccess": true,
  "httpCode": 200
}
```

---

## Enum Categories

### Asset Management (5 enums)

- **AssetTypeEnum**: Main asset categories (Vehicle, Equipment, Site, Phone)
- **AssetStatusEnum**: Asset operational status (Operational, NonOperational, InRepair, NotInstalled)
- **VehicleTypeEnum**: 20 vehicle subtypes (Car, Truck, Van, Boat, etc.)
- **EquipmentTypeEnum**: Equipment types (FuelTank, ElectricGenerator)
- **SiteTypeEnum**: Site types (Coldroom)

### Gateway & Hardware (7 enums)

- **ManufacturerTypeEnum**: Gateway manufacturers (Teltonika, Queclink, GalileoSky, etc.)
- **GatewayCommandEnum**: Commands sent to gateways (Immobilize, Unimmobilize, OpenDoor, etc.)
- **GatewayCounterTypeEnum**: Counter types (Odometer, EngineHours, EngineHoursOnCounter)
- **GatewayFeatureEnum**: Gateway capabilities (TrackingHistorique, Can, VideoStreaming, etc.)
- **GatewayMovementStatusEnum**: Movement states (Parked, Moving, Stopped)
- **GatewayConnectionStatusEnum**: Connection states (SignalLost, Offline, Idle, Active, etc.)
- **OperatorTypeEnum**: Network operators (International, Locale, Caburn, Matooma)

### Accessories & Sensors (4 enums)

- **AccessoryTypeEnum**: 14 accessory types (Immobilizer, Temperature, FuelCapacity, DoorOpening, etc.)
- **AccessoryConnectionEnum**: Connection methods (Wire, Bluetooth, Wifi)
- **SensorTypeEnum**: 22 sensor types (Temperature, Fuel sensors, CAN bus sensors, Ignition, etc.)
- **FuelTypeEnum**: Fuel sensor types (Digital, Analogic)

### User & Customer (5 enums)

- **UserRoleEnum**: System user roles (FleetiSuperAdmin, FleetiAdmin, Customer, Technician, etc.)
- **UserCustomerRoleEnum**: Customer-level roles (Admin, Basic)
- **CustomerBusinessEnum**: Customer types (Business, Individual)
- **CustomerRoleEnum**: Customer permissions (CreateSubCustomer)
- **CustomerRelationTypeEnum**: Customer relationships (Subsidiary, Renter, DealerCustomer)

### Location & Geofencing (2 enums)

- **LocationTypeEnum**: Location types (Geofence, Poi)
- **LocationGeofenceTypeEnum**: Geofence shapes (Circle, Polygon, Sausage)

### Operations & Installation (3 enums)

- **OperationTypeEnum**: Operation types (Installation, GatewayReplacement, GatewayUninstallation)
- **OperationStatusEnum**: Operation workflow states (Pending, Configuration, Ongoing, Done, Closed)
- **OperationConfigurationStatusEnum**: Configuration progress (SimCardConfigured, GatewayConfigured, etc.)

### Reports & Analytics (5 enums)

- **ReportTypeEnum**: Report categories (RmrReport, LocationVisitReport, FuelReport, RentalReport)
- **ReportStateEnum**: Report generation states (Waiting, Loading, Error, Done)
- **ProviderReportEnum**: Provider report types (TripsAndStops, EcoDriving, Geofence, Poi)
- **ProviderTypeEnum**: Data providers (TrackingFleeti, Hiboo)
- **ProviderPlanEnum**: Provider plans (Default, Premium)

### Energy & Fuel (1 enum)

- **EnergyTypeEnum**: Fuel/energy types (Gasoline, Diesel, Electric, Hybrid, etc.)

### Scenarios & Automation (2 enums)

- **ScenarioActionTypeEnum**: Scenario actions (MailNotification)
- **ScenarioRecurrenceTypeEnum**: Recurrence patterns (OneTime, Daily, Weekly, Monthly, Yearly)

### Time & Scheduling (1 enum)

- **DayOfTheWeek**: Day values including special values (Monday-Sunday, Day, Weekday, WeekendDay)

### System & Infrastructure (10 enums)

- **EndpointStatusEnum**: Endpoint states (Active, Suspend, Hold, PreActive, ActiveTest, etc.)
- **EnvironmentEnum**: Environment types (DEV, PR)
- **LogLevel**: Logging levels (Debug, Info, Warn, Error)
- **ResultEnum**: Operation results (Ok, NOk, Neutral)
- **VisitStatusEnum**: Visit states (Pending, Ongoing, Done, Cancelled, MissingReport)
- **StorageAccessTierEnum**: Storage tiers (Hot, Cool, Archive, Premium, Cold)
- **StorageCollectionEnum**: Storage collections (Customers, Users, Operations, Gateways, etc.)
- **EmbeddedModuleActionEnum**: Module actions (Enable, Disable)
- **EmbeddedModuleAuthorizationTypeEnum**: Auth types (ApiKey, UserSession)
- **EmbeddedModuleDisplayMethodEnum**: Display methods (NewTab, Embedded)

---

## Key Insights

### Value Numbering Patterns

- **Sequential (0, 1, 2, 3...)**: Simple sequential numbering
- **Incremental (10, 20, 30...)**: Allows insertion of new values between existing ones
- **Categorized (100, 200, 300...)**: Grouped by category (e.g., GatewayFeatureEnum uses 100s for standard features, 1000+ for video features)

### Localization Support

- **45 enums** total
- **38 enums** have French translations (`fr` field)
- **38 enums** have English translations (`en` field)
- **7 enums** are English-only (typically system/internal enums)

### Visual Assets

- **6 enums** include image URLs for icons:
  - `AssetTypeEnum` (4 images)
  - `AssetStatusEnum` (4 images)
  - `AccessoryTypeEnum` (14 images)
  - `EquipmentTypeEnum` (3 images)
  - `SiteTypeEnum` (2 images)
  - `VehicleTypeEnum` (20 images)
- Images are hosted at: `https://stfleeticommon.blob.core.windows.net/images/enums/`

### Most Complex Enums

1. **SensorTypeEnum**: 22 values (largest enum)
2. **VehicleTypeEnum**: 20 values
3. **AccessoryTypeEnum**: 14 values
4. **UserRoleEnum**: 9 values
5. **EnergyTypeEnum**: 10 values

---

## Usage in Specifications

When drafting feature specifications:

1. **Reference the JSON file** for exact enum values and translations
2. **Use numeric values** in API contracts (backend uses integers)
3. **Use enum names** in code examples (e.g., `Vehicle`, `Operational`)
4. **Reference translations** for UI display (use `fr` or `en` based on locale)
5. **Include image URLs** when displaying enum icons in the UI

### Example: Asset Type Selection

```json
{
  "assetType": 10,
  "vehicleType": 3
}
```

**Field values:**
- `assetType`: See `docs/enums/response.json` - `AssetTypeEnum`
  - `10` = Vehicle
  - `20` = Equipment
  - `30` = Site
  - `40` = Phone
- `vehicleType`: See `docs/enums/response.json` - `VehicleTypeEnum`
  - `3` = Truck
  - `1` = Car
  - `7` = Van
  - (20 total vehicle types)

---

## Related Documentation

- **[Schema Specification](../specifications/schema-specification.md)**: Telemetry schema with enum references
- **[Telemetry System Specification](../specifications/telemetry-system-specification.md)**: System specification
- **[Status Rules](../specifications/status-rules.md)**: Status computation (uses enum values)

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-XX  
**Status**: ✅ Validated  
**Source**: `docs/enums/README.md`, `docs/enums/response.json`






