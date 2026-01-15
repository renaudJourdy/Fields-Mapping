# Ingesting Provider Data

## Provider Agnostic

The ingestion pipeline should be provider agnostic. It means that we need a way to ingest not only the data of Navixy but also other providers like OEM provider. Data Forwarding has been chosen as a technology to ingest Navixy Data but other kind of technology can be chosen for other provider (data polling, webhook…) without affecting the working of already implemented providers.

One customer can be attached to one provider or multiple providers. The system should be done in a way that one customer can be linked with multiple providers and still have flawlessly its telemetry data available based on mapping configuration files defined. 

## Navixy: Data Forwarding

Navixy is the first provider we want to implement in our system. It will be the first block for our Fleeti telemetry-agnostic provider system. The data forwarding is a solution proposed by Navixy to forward us with the raw packet telemetry as soon as the telemetry arrives in their server. Here, the objective for me is not to have a technical implementation specification but to describe what the Fleeti product system needs. 
What I need in the end is to list some features for the developers and the product needs some proper documentation that describe how to connect to Navixy for a specific customer using data forwarding. We should have this documented in the wiki in the technical documentation. We need a way as well to be able to stop the data forwarding for a specific customer to delete it, and we need an easy way as well to add in bulk multiple customers. 

To manage customers through data forwarding, we need to have a way to:

- Manually add a single customer
- Manually add multiple customers
- Manually remove or suspend one customer
- Manually remove multiple customers

The end feature, which I will not specify yet but should be present as a feature, is that we need a way to have, without doing any manual implementation, a way that's based on our customer-based system that's enabled to have a synchronization and creating the pipeline for the data forwarding. For example, on Fleeti Admin, we add a new customer and then, as soon as the new customer is added to our system, we just open the data forwarding possibility.

One other important aspect as well for the data forwarding is that we need a way to know that the data forwarding stopped to function. So maybe we can have a partial non-functioning and our total non-functioning based on for example if Navixy totally crashes, then we need a way to be aware of it. This is one of the features as well just to have a system that lets us know that the data forwarding has stopped. 

Something that is complimentary to be aware of is data forwarding has stopped. It is a way to manually recover not received data. So if we know that we have lost at a specific point of time, then we need to have a tool or an ability to automatically, or maybe firstly manually recover not received data. We have raw data read API called from Navixy that can serve this purpose.

First, I need to confirm with Navixy that if something is wrong on their side, how the data forwarding behaves? Do we receive when the system has been recovered from Navixy's side? Do we know and do we receive all the data in a row, or should we fetch them or pull them directly using API call?

This recovery system should fit. We need to detect the last point in time where we don't have received any data in the future. We need to make the APHQL from this date to the current date, and all the fetched fields should be. I don't know if we need to rebuild the raw packet log based on the API received data and to push all these rebuilt raw packet logs and send them to our ingestion system to follow the same ingestion workflow and passing of the data, mapping rules, etc. or do we need to have something that from API direct to our database. This is something I'm not sure yet. 

When the data has been received in the backend, we need a way to extract what is necessary for the transformation pipeline to be transformed. So we need to here in this ingestion layer a way to pass the data into multiple fields that can be understood by the transformation pipeline. Every time we receive a raw packet from a provider or we fetch it manually, then we store raw records inside the cold storage. So basically, we receive all fetch the data manually and we store the raw data in cold storage to be easily retrieved or recomputed later. 

---

Quick review:

- We have a documentation on how to manage customer connection for data forwarding
- We have a way do detect data forwarding stop functionning and a way to recover lost packet
- An architecture that allow Fleeti to integrate a new provider with different technology without affecting implemented providers
- The data is parsed and ready to be mapped
- Provider Raw telemetry is store in cold storage and sent to the transformation pipeline

---

# Transformation pipeline

When the telemetry arrives independently of the provider, we need to map it into Fleeti Fields. In this sense, each raw packet received from providers is mapped into a Fleeti Field format. So basically, the transformation pipeline receives a file in JSON format and based on the provider gateway, we execute the file of the provider. 

So for now, we only have a unique configuration file for all assets across Navixy provider. But the system should be architected to be able to have a dedicated configuration file assigned to:

- The entire fleet of Navixy provider or any provider at the customer level
- A group of asset level
- At the single asset level

The transformed telemetry is saved in storage or databases. Each time a record is processed, we should have a correspondent row in the database. 

---

Quick review:

- Depending on the provider of the received telemetry, we map it into Fleeti Fields by executing a YAML configuration file.
- The record is transformed into Fleeti Fields Telemetry and stored into database (see storage stragy next)
- The execution of the configuration file is common for all assets of a same provider for now but the architecture is ready to have an adaptation at the customer, group of assets or assets level

---

# Storage Strategy

I'm not sure yet how to deal with the storage strategy, and I'm expecting a lot from you actually. So basically, what I have in mind is that every received packet will be saved in cold storage for history purposes. For recomputation purposes, for troubleshoot purposes, we will need to have raw recalls just to make sure that if we have integrated new fields and we want to recompute it, we have a way to do it. 

This said, we will have hot storage field that for example when the user will be on FleetiOne as a web application or mobile application, when he will see the map, the map should update it accordingly live. Everything that would be displayed for the markers should be in hot storage. Everything which is necessary for the asset list display or the asset details display should be in warm storage. This is actually my opinion, but I want to have the best strategy. I'm a newbie here, so I'm expecting from you that you are suggesting something great for my need. 

Then we need to define a strategy based on, for example, when we will have one month of hot storage and warm storage, we should maybe put data older than one month into cold storage and make it available from API or maybe from the front end when seeing the history. But it seems that we don't need it anymore in hot and warm storage. 

I am expecting from the development team to evaluate the difference between keeping one year of history in hot and warm storage in comparison to putting them into cold storage, or I mean, to have only one month per asset in hot and warm storage. I want to understand what is the difference of cost by having them in databases rather than in cold storage.

And I am expecting as well from the developers to, for example, by fetching one month of history. In cold storage, what is the delay for it? And what is the performance for hot and warm storage aggregation? If we have hot and warm storage and we aggregate the data, it should be much more performant than in cold storage, but I need to have metrics for this.

So the first decision would be to keep data in hot and warm storage for one month and then move it to cold storage. And as well, I'd like to have some investigation for warm vs hot storage. What is the difference in performance? Should we only have hot storage? What is the price difference? And performance.

---

# Troubleshooting

Another aspect as well that we will need is to be able to rebuild what happened in the mapping. So for example, we received a row packet and based on a lot of conditions for all fleeting fields, we will either select CAN speed or OBD  speed and so on for all the other fleeting fields. But in case that the customer is complaining about the results, we will need to investigate about the mapping that have been chosen. If we don't have either a tool to investigate based on raw records or we don't have a plain text. So for example, what I see is two things: Either that based on the configuration file used based on the raw records having a tool that allows us to rebuild for a specific period of time the mapping conditions and see that for example having the detail of how the fleeting field speed have been mapped or calculated. The option 2 is maybe to create another cold storage database. By having any, for any fields, I mean during one year, we will keep in cold storage a plaintext of a correspondence and the value and where the value comes from. If it is a direct mapping, we can have a direct provider field’s name. If it is calculated, then we can have maybe all the parameters for the calculation and to have the details of it. So I will also need your help in this. 

---

# Provider Priority Configuration Specification

[Provider Priority Configuration Specification](https://www.notion.so/Provider-Priority-Configuration-Specification-2e23e766c90180ee881bf9ad4588fa7e?pvs=21)

---

# Consumming Data

Now that we have received data from the provider, we will need to consume it. Based on the subscription from the front-end application (that can be web or mobile), we need to provide consolidated data. Some of the data have been already illustrated in the dedicated page, but I'm expecting from the development team that they draft a proper documentation of the WebSocket contract and to make it up to date in the Notion Wiki. So basically it's a combination of Fleeti telemetry and asset service data. And maybe in some cases some KPI data that came from a different source as well. So, we'll have to create as well features indicating that we need to have everything regarding the subscription of the WebSocket, so it means that the subscription acknowledgement from the server, data update, error handling, security as well. As soon as the data is received from the provider, we will update it and send it to the relevant front-end application. 

When the data is requested by API, we can have either snapshots or history. Normally for the snapshot, it's like it will be stored in hot and warm storage, but we should aggregate this data and aggregate asset service data as well and provide it in reasonable time slots to the customer. We have as well a difference between the Snapshot and History API call depending on if it is a customer that needs the data or if it is a Fleeti Admin for example. For troubleshoot purposes, a Fleeti admin user needs more data, so we will have some troubleshoot fields that we need to keep hidden for the customer because they are useless for them but useful for us. For the history endpoints, it is the same regarding customer request or Fleeti admin request. You need to have some differences, but there we will need to rebuild everything and consolidate maybe some combination of storage (cold storage data alongside with hot and warm storage), so we need to aggregate everything. I think that limiting the history data to one month is great for now.