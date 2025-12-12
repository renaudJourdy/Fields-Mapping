# 🎯 Purpose

This document provides a **formal specification** of the raw AVL packet format forwarded by Navixy's Data Forwarding feature.

It defines the exact structure, field positions, data types, formats, and parsing rules for the `#D#` packet format used by Teltonika trackers.

---

# 1️⃣ Packet Format Overview

## Structure

Raw AVL packets are **single-line ASCII strings** starting with `#D#` and containing semicolon-separated fields.

**Format:**
```
#D#<date>;<time>;<lat_raw>;<lat_hemisphere>;<lng_raw>;<lng_hemisphere>;<speed>;<heading>;<altitude>;<satellites>;<hdop>;<inputs>;<outputs>;<adc>;<ibutton>;<params>
```

## Delimiters

- **Field separator:** Semicolon (`;`)
- **ADC values separator:** Comma (`,`) - within the ADC field only
- **Params separator:** Comma (`,`) - within the params section only
- **Param format:** `NAME:TYPE:VALUE` (colon-separated)

---

# 2️⃣ Field-by-Field Specification

## Field Position Table

| Position | Field Name | Format | Data Type | Required | Example | Notes |
|----------|------------|--------|-----------|----------|---------|-------|
| 0 | **Packet Header** | `#D#` | String | Yes | `#D#` | Always present, marks start of packet |
| 1 | **Date** | `DDMMYY` | String | Yes | `061025` | Device date (06 October 2025) |
| 2 | **Time** | `HHMMSS` | String | Yes | `104310` | Device time (10:43:10 UTC) |
| 3 | **Latitude Raw** | `DDMM.MMMM` | String | Yes | `2017.1096` | Degrees and decimal minutes |
| 4 | **Latitude Hemisphere** | `N\|S` | String | Yes | `S` | North or South |
| 5 | **Longitude Raw** | `DDDMM.MMMM` | String | Yes | `05725.9927` | Degrees and decimal minutes |
| 6 | **Longitude Hemisphere** | `E\|W` | String | Yes | `E` | East or West |
| 7 | **Speed** | Integer | Integer | Yes | `78` | Speed in km/h |
| 8 | **Heading** | Integer | Integer | Yes | `143` | Course/heading in degrees (0-359) |
| 9 | **Altitude** | Integer | Integer | Yes | `243` | Altitude/height in meters |
| 10 | **Satellites** | Integer | Integer | Yes | `15` | Number of satellites used |
| 11 | **HDOP** | Integer or `NA` | Integer\|String | Yes | `NA` | Horizontal Dilution of Precision |
| 12 | **Inputs** | Integer | Integer | Yes | `9` | Bitmask of digital inputs |
| 13 | **Outputs** | Integer | Integer | Yes | `1` | Bitmask of digital outputs |
| 14 | **ADC** | Comma-separated floats | String | Yes | `0.172,0.172` | Analog-to-Digital Converter values |
| 15 | **iButton** | Hex string or `NA` | String | Yes | `NA` | iButton identifier or `NA` |
| 16 | **Params** | Comma-separated `NAME:TYPE:VALUE` | String | Yes | `EVENT:1:2,avl_io_1:1:1,...` | Variable-length parameters section |

---

# 3️⃣ Field Details

## 3.1 Date and Time (Fields 1-2)

**Format:** `DDMMYY;HHMMSS`

- **Date:** `DDMMYY` (Day, Month, Year - 2 digits each)
  - Example: `061025` = 06 October 2025
- **Time:** `HHMMSS` (Hour, Minute, Second - 2 digits each, 24-hour format)
  - Example: `104310` = 10:43:10 UTC

**Parsing Rules:**
- Always interpreted as **UTC** timezone
- Combined to form ISO 8601 timestamp: `YYYY-MM-DDTHH:MM:SSZ`
- Example: `061025;104310` → `2025-10-06T10:43:10Z`

---

## 3.2 Coordinates (Fields 3-6)

**Format:** `DDMM.MMMM;N|S;DDDMM.MMMM;E|W`

- **Latitude Raw:** `DDMM.MMMM`
  - `DD` = degrees (00-90)
  - `MM.MMMM` = decimal minutes (00.0000-59.9999)
  - Example: `2017.1096` = 20°17.1096' South

- **Latitude Hemisphere:** `N` or `S`
  - Determines sign for decimal degrees conversion

- **Longitude Raw:** `DDDMM.MMMM`
  - `DDD` = degrees (000-180)
  - `MM.MMMM` = decimal minutes (00.0000-59.9999)
  - Example: `05725.9927` = 57°25.9927' East

- **Longitude Hemisphere:** `E` or `W`
  - Determines sign for decimal degrees conversion

**Conversion Formula:**
```
decimal_degrees = DD + (MM.MMMM / 60)
if hemisphere == 'S' or hemisphere == 'W':
    decimal_degrees = -decimal_degrees
```

**Example:**
- `2017.1096;S` → `-20.28516` decimal degrees
- `05725.9927;E` → `57.43321` decimal degrees

---

## 3.3 Navigation Fields (Fields 7-11)

| Field | Name | Range | Unit | Notes |
|-------|------|-------|------|-------|
| **Speed** | Integer | 0-255+ | km/h | Vehicle speed |
| **Heading** | Integer | 0-359 | degrees | Course/direction (0=North, 90=East, 180=South, 270=West) |
| **Altitude** | Integer | -32768 to 32767 | meters | Height above sea level (can be negative) |
| **Satellites** | Integer | 0-99 | count | Number of GPS satellites used for fix |
| **HDOP** | Integer or `NA` | 0-99 or `NA` | unitless | Horizontal Dilution of Precision (lower is better) |

**Special Values:**
- `HDOP` can be `NA` if not available
- `Altitude` can be negative (below sea level)

---

## 3.4 Digital I/O (Fields 12-13)

**Format:** Integer (bitmask)

- **Inputs:** Bitmask representing digital input states
  - Each bit represents one input channel (bit 0 = channel 1, bit 1 = channel 2, etc.)
  - Example: `9` = binary `1001` = channels 1 and 4 are active

- **Outputs:** Bitmask representing digital output states
  - Same bit encoding as inputs
  - Example: `1` = binary `0001` = channel 1 is active

**Bit Decoding:**
```
Channel N = (value >> (N-1)) & 1
```

**Example:**
- `inputs=9` → binary `1001` → `{1:1, 2:0, 3:0, 4:1}`
- `outputs=1` → binary `0001` → `{1:1}`

---

## 3.5 Analog Values (Field 14)

**Format:** Comma-separated floating-point values

- **ADC:** Analog-to-Digital Converter readings
  - Format: `value1,value2,value3,...`
  - Values are floating-point numbers
  - May be empty (no ADC values)
  - Example: `0.172,0.172` = two ADC channels with value 0.172

**Parsing Rules:**
- Split by comma (`,`)
- Convert each value to float
- Store as array: `[0.172, 0.172]`
- Empty field → empty array `[]`

---

## 3.6 iButton (Field 15)

**Format:** Hexadecimal string or `NA`

- **Present:** 16-character hex string (e.g., `BA0000002B4D4E01`)
- **Absent:** `NA`

**Parsing Rules:**
- If `NA` → store as `null` in JSON
- If hex string → store as string value
- Case-insensitive (typically uppercase)

---

## 3.7 Parameters Section (Field 16)

**Format:** Comma-separated `NAME:TYPE:VALUE` pairs

**Structure:**
```
NAME1:TYPE1:VALUE1,NAME2:TYPE2:VALUE2,NAME3:TYPE3:VALUE3,...
```

**Parameter Types:**

| Type Code | Data Type | Description | Example Values |
|-----------|-----------|-------------|----------------|
| `1` | Integer | Signed integer (int/long) | `2`, `893204200000`, `-1` |
| `2` | Double | Floating-point number | `13.642`, `0.0`, `221257.7` |
| `3` | String | Text string | `"0"`, `"BA0000002B4D4E01"` |

**Common Parameters:**

- **Event Parameters:**
  - `EVENT:1:2` - Event type (2=track, 11-18=input, 111-118=output, etc.)

- **AVL I/O Parameters:**
  - `avl_io_1:1:1` - AVL I/O element 1 (type 1 = integer, value = 1)
  - `avl_io_100:1:13259` - AVL I/O element 100
  - Pattern: `avl_io_<number>:<type>:<value>`

- **Device Parameters:**
  - `battery_level:1:92` - Battery level percentage
  - `board_voltage:2:13.642` - Board voltage in volts

- **CAN Bus Parameters:**
  - `can_speed:1:79` - CAN bus speed
  - `can_rpm:1:2667` - Engine RPM
  - `can_fuel_litres:1:980` - Fuel level in liters
  - Pattern: `can_<parameter>:<type>:<value>`

- **Other Parameters:**
  - `gsm.signal.csq:1:19` - GSM signal strength
  - `hw_mileage:2:46293.146` - Hardware mileage
  - `moving:1:1` - Moving state (0=stopped, 1=moving)

**Parsing Rules:**
1. Split by comma (`,`)
2. For each parameter:
   - Split by colon (`:`) → `[NAME, TYPE, VALUE]`
   - Parse TYPE as integer (1, 2, or 3)
   - Parse VALUE according to TYPE:
     - Type 1: Parse as integer
     - Type 2: Parse as float
     - Type 3: Keep as string
3. Store in JSON as: `{ "NAME": { "type": TYPE, "value": VALUE } }`

**Example:**
```
EVENT:1:2,avl_io_1:1:1,board_voltage:2:13.642
```

Parses to:
```json
{
  "EVENT": { "type": 1, "value": 2 },
  "avl_io_1": { "type": 1, "value": 1 },
  "board_voltage": { "type": 2, "value": 13.642 }
}
```

---

# 4️⃣ Complete Example

## Raw Packet
```
#D#061025;104310;2017.1096;S;05725.9927;E;78;143;243;15;NA;9;1;0.172,0.172;NA;EVENT:1:2,avl_io_1:1:1,board_voltage:2:13.642
```

## Parsed Structure

| Field | Value | Parsed |
|-------|-------|--------|
| Header | `#D#` | Packet marker |
| Date | `061025` | 2025-10-06 |
| Time | `104310` | 10:43:10 UTC |
| Lat Raw | `2017.1096` | 20°17.1096' |
| Lat Hem | `S` | South |
| Lng Raw | `05725.9927` | 57°25.9927' |
| Lng Hem | `E` | East |
| Speed | `78` | 78 km/h |
| Heading | `143` | 143° |
| Altitude | `243` | 243 m |
| Satellites | `15` | 15 sats |
| HDOP | `NA` | null |
| Inputs | `9` | Binary: 1001 (channels 1,4) |
| Outputs | `1` | Binary: 0001 (channel 1) |
| ADC | `0.172,0.172` | [0.172, 0.172] |
| iButton | `NA` | null |
| Params | `EVENT:1:2,avl_io_1:1:1,board_voltage:2:13.642` | See below |

## Parsed JSON (Excerpt)
```json
{
  "msg_time": "2025-10-06T10:43:10Z",
  "lat": {
    "raw": "2017.1096",
    "hemisphere": "S",
    "decimal_degrees": -20.28516
  },
  "lng": {
    "raw": "05725.9927",
    "hemisphere": "E",
    "decimal_degrees": 57.43321
  },
  "speed": 78,
  "heading": 143,
  "alt": 243,
  "satellites": 15,
  "hdop": null,
  "inputs": 9,
  "outputs": 1,
  "adc": [0.172, 0.172],
  "ibutton": null,
  "params": {
    "EVENT": { "type": 1, "value": 2 },
    "avl_io_1": { "type": 1, "value": 1 },
    "board_voltage": { "type": 2, "value": 13.642 }
  }
}
```

