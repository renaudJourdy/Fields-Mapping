// Q (Renaud): how to handle multiple gateways in an asset?
// Q (Renaud/investigate): does DF send (un)calibrated data? ex: in fuel tank cm or liters

// We need to keep track of gateway ID somehow to handle multiple gateways sending data
Table fleeti_telemetry {
  id string [primary key]
  asset_id string [not null]
  trip_id string [null] // optional FK -> fact_trip.id (NULL when no ongoing trip)
  
  // location data
  latitude number [not null] // in degrees
  longitude number [not null] // in degrees
  altitude number [not null] // in meters
  heading number [not null] // in degrees
  precision_fix_quality enum [not null]
  satellites number [not null]
  hdop number [not null]
  pdop number [not null]
  // end location data

  // diagnostics data
  // might be extended further
  dtc_count number [not null]
  is_dtc_on boolean [not null]
  // end diagnostics data

  // motion data
  speed number [not null] // km/h
  is_moving boolean [not null]
  // end motion data
  sensor_telemetry_id string [not null]
  counter_telemetry_id string [not null]
  status_id string [not null]
  driver_id string [not null, unique]
  input_id string [not null, unique]
  output_id string [not null, unique]
  created_at timestamp [not null]
  device_update_time timestamp [not null]
  fleeti_receiving_time timestamp [not null]
}

// each record is related to ONE telemetry record only
// (Q: abdullah) do we need to store statuses in the DB historically or just compute them?
// how to optimize storage for columns
Table status_telemetry {
  id string [primary key]
  family enum [not null] // connectivity, immobilization, engine, or transit
  code enum [not null] //"offline", "immobilized", "running", "in_transit", "parked", "online"
  compatible boolean [not null]
  telemetry_id string [not null] // 1:N relation with fleeti_telemetry
  is_top_status boolean [not null]
  created_at timestamp [not null]
}



// Q: will we store this metadata in mongo? "same as driver data"
// Q: might need more data
// Q (hanya): geofence data in DF packet or not?
Table geofence {
  id string [primary key]
  name string [not null]
  customer_reference string [not null]
  created_by string [null]
  created_at timestamp [not null]
  updated_at timestamp [not null]
}

// Junction table for N:M relation between geofences and telemetry tables
Table fleeti_telemetry_geofences {
  telemetry_id string [not null]
  geofence_id string [not null]
  created_at timestamp [not null]
  indexes {
    (telemetry_id, geofence_id) [unique]
    (telemetry_id)
    (geofence_id)
  }
}

// Q: will we use the existing trips table or calculate the trip using telemetry provided via DF?
// Answer: We can't use the existing one as it syncs every hour

// ongoing trips/ last hour trips: redis, historical trips: postgres
Table trip_telemetry {
  id string [primary key]
  start_time timestamp [not null]
  mileage number [not null]
}


// Q (Renaud): how many inputs/outputs can exist?
// if scalable not fixed do as sensors (type, value, etc.)
Table input_telemetry{
  id string [primary key]
  number number [not null]
  is_on boolean [not null]
}

Table output_telemetry{
  id string [primary key]
  number number [not null]
  is_on boolean [not null]
}

// restructure to have a unit, type, and timestamp and change to 1:N relation
Table sensor_telemetry {
  id string [primary key]
  //IMPORTANT 
  //Q (Renaud/investigate): is the sensor/counter id sent in the DF packet? 
  sensor_id string [not null]
  sensor_type enum [not null] //same as enum in mongo
  unit string [not null]
  value number [not null]
}

Table counter_telemetry {
  id string [primary key]
  //IMPORTANT 
  //Q (Renaud/investigate): is the sensor/counter id sent in the DF packet? 
  counter_id string [not null]
  counter_type enum [not null] //same as enum in mongo
  unit string [not null]
  value number [not null]
}

// IMPORTANT
//Q: should this live in Mongo too since it's metadata??
Table driver_metadata {
  id string [primary key]
  name string [not null]
  key string [not null]
  // add other fields from legacy page
}



// odometer is a counter not sensor
// counters table should have type;, value, unit, asset ID

// TODO (still to be specified by Yannick)
//Table events_telemetry {
//  id string [primary key]
//}

Ref: "fleeti_telemetry"."status_id" < "status_telemetry"."id"

Ref: "fleeti_telemetry_geofences"."telemetry_id" > "fleeti_telemetry"."id"
Ref: "fleeti_telemetry_geofences"."geofence_id" > "geofence"."id"

Ref: "fleeti_telemetry"."trip_id" > "trip_telemetry"."id"

Ref: "fleeti_telemetry"."sensor_telemetry_id" < "sensor_telemetry"."id"
Ref: "fleeti_telemetry"."counter_telemetry_id" < "counter_telemetry"."id"



Ref: "fleeti_telemetry"."input_id" < "input_telemetry"."id"
Ref: "fleeti_telemetry"."output_id" < "output_telemetry"."id"

Ref: "fleeti_telemetry"."driver_id" > "driver_metadata"."id"
