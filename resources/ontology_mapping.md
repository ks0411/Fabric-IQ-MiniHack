# Ontology Mapping Reference: Domain Model → Fabric

This document maps the workshop domain concepts to the Fabric Ontology implementation.

---

## Entity Type Mapping

### Domain Concepts → Fabric Entity Types

| Concept 		| Fabric Entity Type | Source Table 	 | Key 			 	 |
|---			|---				 |---				 |---				 |
| Trip 			| Trip 				 | `trips` 			 | `trip_id` 		 |
| Location 		| Zone 				 | `zones` 			 | `location_id` 	 |
| PaymentType 	| PaymentType 		 | `payment_types` 	 | `payment_type_id` |
| RateType 		| RateCode           | `rate_codes` 	 | `rate_code_id` 	 |
| Borough 		| Borough 			 | `dim_borough` 	 | `borough_name`    |
| ZoneType 		| ZoneType 			 | `dim_zone_type` 	 | `zone_type` 		 |
| TripType 		| TripType 			 | `dim_trip_type` 	 | `trip_type` 		 |
| TimeContext 	| TimeContext 		 | `dim_time_context`| `time_context` 	 |
| BusinessRule 	| BusinessRule 		 | `business_rules`  | `rule_name` 		 |
| Vendor 		| (Property of Trip) | `trips.vendor_id` | — 				 |

### Derived Classifications → Fabric Implementation

| Classification   | Type 		| Fabric Implementation 						|
|---			   |---			|---											|
| Manhattan 	   | Borough 	| `dim_borough.borough_name = 'Manhattan'`      |
| Brooklyn 		   | Borough 	| `dim_borough.borough_name = 'Brooklyn'` 		|
| Queens 		   | Borough 	| `dim_borough.borough_name = 'Queens'` 		|
| Bronx 		   | Borough 	| `dim_borough.borough_name = 'Bronx'` 			|
| Staten Island    | Borough 	| `dim_borough.borough_name = 'Staten Island'`  |
| CreditCard 	   | PaymentType| `payment_types.payment_type_id = 1` 	 		|
| Cash 			   | PaymentType| `payment_types.payment_type_id = 2` 			|
| StandardRate 	   | RateType 	| `rate_codes.rate_code_id = 1` 				|
| JFKFlatRate      | RateType 	| `rate_codes.rate_code_id = 2` 				|
| NewarkFlatRate   | RateType 	| `rate_codes.rate_code_id = 3` 				|
| AirportTrip      | TripType 	| `dim_trip_type.trip_type = 'Airport'` 		|
| CommuteTrip      | TripType 	| `dim_trip_type.trip_type = 'Commute'` 		|
| LongDistanceTrip | TripType 	| `dim_trip_type.trip_type = 'Long Distance'` 	|
| ShortTrip        | TripType 	| `dim_trip_type.trip_type = 'Short'` 			|
| NightTrip 	   | TripType 	| `dim_trip_type.trip_type = 'Night'` 			|
| WeekendTrip 	   | TripType 	| `dim_trip_type.trip_type = 'Weekend'` 		|

### Zone Types → Fabric Implementation

| Zone Type 			| Fabric Implementation 															  	  |
|---					|---																				  	  |
| Airport 				| `dim_zone_type.zone_type = 'Airport'` and `Zone -> ZoneType` relationship 		  	  |
| Business District 	| `dim_zone_type.zone_type = 'Business District'` and `Zone -> ZoneType` relationship 	  |
| Tourist Zone 			| `dim_zone_type.zone_type = 'Tourist Zone'` and `Zone -> ZoneType` relationship 	      |
| Residential 			| `dim_zone_type.zone_type = 'Residential'` and `Zone -> ZoneType` relationship           |
| Transit Hub 			| `dim_zone_type.zone_type = 'Transit Hub'` and `Zone -> ZoneType` relationship 	      |
| Entertainment District| `dim_zone_type.zone_type = 'Entertainment District'` and `Zone -> ZoneType` relationship|

---

## Property Mapping

### Relationships → Fabric Relationships

| Relationship 						| Domain → Range 			| Fabric Relationship 		| Source → Target 			|
|---								|---						|---						|---			  			|
| hasPickupLocation					| Trip → Zone 				| `hasPickupZone` 			| Trip → Zone 				|
| hasDropoffLocation 				| Trip → Zone 				| `hasDropoffZone` 			| Trip → Zone 				|
| hasPaymentMethod 					| Trip → PaymentType 		| `paidWith` 				| Trip → PaymentType 		|
| hasRateType 						| Trip → RateType 			| `usesRate` 				| Trip → RateCode 			|
| inBorough 						| Zone → Borough 			| `inBorough` 				| Zone → Borough 			|
| hasZoneType 						| Zone → ZoneType 			| `hasZoneType` 			| Zone → ZoneType 			|
| operatedBy 						| Trip → Vendor 			| (Property on Trip entity) | `trips.vendor_id` 		|
| hasTripType 						| Trip → TripType 			| `hasTripType` 			| Trip → TripType 			|
| occursIn 							| Trip → TimeContext 		| `occursIn` 				| Trip → TimeContext 		|
| appliesToPaymentType 				| BusinessRule → PaymentType| `appliesToPaymentType` 	| BusinessRule → PaymentType|
| appliesToRateCode 				| BusinessRule → RateCode 	| `appliesToRateCode` 		| BusinessRule → RateCode 	|

### Entity Properties → Fabric Entity Properties

| Property 					| Fabric Entity | Fabric Property 		| Source Column 			|
|---						|---			|---			  		|---						|
| fareAmount 				| Trip 			| `fare_amount`   		| `trips.fare_amount` 		|
| tipAmount 				| Trip 			| `tip_amount`    		| `trips.tip_amount` 		|
| totalAmount 				| Trip 			| `total_amount`  		| `trips.total_amount` 		|
| tripDistance 				| Trip 			| `trip_distance` 		| `trips.trip_distance` 	|
| pickupDatetime 			| Trip 			| `pickup_datetime` 	| `trips.pickup_datetime` 	|
| dropoffDatetime 			| Trip 			| `dropoff_datetime` 	| `trips.dropoff_datetime`  |
| passengerCount 			| Trip 			| `passenger_count` 	| `trips.passenger_count` 	|
| zoneName 					| Zone 			| `zone_name` 			| `zones.zone_name` 		|
| locationId 				| Zone 			| `location_id` 		| `zones.location_id` 		|

### Metadata and Rules → Fabric Implementation

| Metadata or Rule 			| Purpose 							| Fabric Equivalent 								|
|---						|---								|---												|
| Table mapping 			| Links entity to SQL table 		| Data binding (automatic) 							|
| Column mapping 			| Links property to SQL column 		| Property binding (automatic) 						|
| Join mapping 				| Defines join condition 			| Relationship source/target columns 				|
| Business context 			| Business explanation 				| Enriched table columns + Agent instructions 		|
| Business rule 			| Data quality or domain rule 		| `business_rules` entity + relationships 			|
| Classification condition  | Trip type classification 			| `v_trip_classification` view + Agent instructions |
| Glossary term 			| Business glossary link 			| Table/column descriptions 						|
| Unit 						| Unit of measurement 				| Agent instructions 								|
| Payment code 				| Payment type numeric code 		| `payment_type_id` property 						|
| Rate code 				| Rate type numeric code 			| `rate_code_id` property 							|
| Borough code 				| Borough string code 				| `borough` property 								|

---

## Business Rule Mapping

| Rule 					 | Fabric Implementation 					     		|
|---					 |---   												|
| TipAnalysisRule 		 | `business_rules` row + Agent instruction #1 			|
| AirportTripRule 		 | `business_rules` row + Agent instruction #3 			|
| ManhattanDominanceRule | `business_rules` row + Agent instruction #2 			|
| PeakHoursRule 		 | `business_rules` row + Agent instruction #8 			|
| RevenueCalculationRule | `business_rules` row + Agent instruction #7 			|
| TripClassificationRule | `v_trip_classification` view + Agent instruction #6  | 
| TipPatternRule 		 | `business_rules` row + Agent instruction #1 			|
| DemandPredictionRule 	 | `business_rules` row + Agent instruction #2, #8 		|
| RevenueOptimizationRule| `business_rules` row + Agent instruction #7 			|
| ZonePerformanceRule 	 | `business_rules` row + Agent instruction #5 			|

---

## Query Pattern Mapping

| Pattern 						| Fabric Equivalent 				|
|---							|---								|
| RevenueByBoroughPattern 		| `v_revenue_by_borough` view 		|
| TripsByPaymentPattern 		| `v_payment_analysis` view 		|
| AirportTripAnalysisPattern 	| `v_airport_analysis` view 		|
| TimeContextAnalysisPattern 	| `v_time_analysis` view 			|
| TripClassificationPattern 	| `v_trip_classification` view 		|

---

## Zone Instance Mapping

| Instance 					| location_id 		| Zone Type 	| Fabric Property 						 |
|---						|---				|---			|---									 |
| JFKAirport 				| 132 				| Airport 		| `zone_type = 'Airport'` 				 |
| LaGuardiaAirport 			| 138 				| Airport 		| `zone_type = 'Airport'` 				 |
| NewarkAirport 			| 1 				| Airport 		| `zone_type = 'Airport'` 				 |
| MidtownCenter 			| 161 				| Business 		| `zone_type = 'Business District'` 	 |
| MidtownEast 				| 162 				| Business 		| `zone_type = 'Business District'` 	 |
| MidtownNorth 				| 163 				| Business 		| `zone_type = 'Business District'` 	 |
| MidtownSouth 				| 164 				| Business 		| `zone_type = 'Business District'` 	 |
| TimesSquare 				| 230 				| Tourist 		| `zone_type = 'Tourist Zone'` 			 |
| CentralPark 				| 43 				| Tourist 		| `zone_type = 'Tourist Zone'` 			 |
| FinancialDistrictNorth 	| 87 				| Business 		| `zone_type = 'Business District'` 	 |
| PennStation 				| 186 				| Transit 		| `zone_type = 'Transit Hub'` 			 |
| EastVillage 				| 79 				| Entertainment | `zone_type = 'Entertainment District'` |
| WestVillage 				| 249 				| Entertainment | `zone_type = 'Entertainment District'` |
| UpperEastSideNorth 		| 236 				| Residential 	| `zone_type = 'Residential'` 			 |

---

## Current Limitations and Workarounds

| Fabric Limitation 							| Impact 								| Workaround 										|
|---											|---									|---												|
| Entity type inheritance not supported 		| Cannot model subtype hierarchies 		| Flat entity types + property-based classification |
| GQL only 										| No SPARQL support 					| Use the visual GQL query builder 					|
| No constraint language 						| Cannot define formal restrictions 	| Encode rules in agent instructions 				|
| No built-in reasoner 							| No automatic inference 				| Use agent reasoning + derived columns 			|
| Time-based classification is not native 		| Requires custom logic 				| `v_time_analysis` view 							|
| Multiple type membership 						| Instances cannot be multiple types 	| Use multiple properties or multi-value fields 	|
