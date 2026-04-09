# Company Enrichment Layer
For this system design I considered these following topics as major:
1. Primary representation of the Company's within the system
2. Identity resolution mechanism for deduplication
3. Raw and Processed data seperation
4. Identificaiton of useful areas for analytics and outbound



### Primary representation of the Company & Identity Resolution
I first define a canonical company entity for this system. This entity's job is to define a single **company_id** for different name representatives. This way for example: Microsoft, Microsoft Corp and Microsoft Coorporation will have same and single company_id. This way I can keep company related fields independently from the provider. 

Example fields to locate:
- company_id
- canonical_name
- primary_domain
- website_url
- linkedin_url
- country
- created_at
- updated_at

The aim of this entity is to yield a single answer to the question "Who is this company?" regardless of the enrichment provider. 

To keep this entity as solid, I also design a layer for **identity resolution** or **alias layer**. In this layer I use a lookup/alias table. I keep name variants of the different companies, normalized domains, external provider company_id's and other useful matching-signals. This way variants like Microsoft, Microsoft Corp and Microsoft Coorporation will glued to same canonical company record. But for this layer to be actually meaningful, instead of static lookup logics and catch unseen-variants I combine multiple rules like: domain-matching, normalized website comparision, LinkedIn URL match, external id matching and even fuzzy name matching logics should be considered. Because it's important verify that we are actually working with the right company as we intended. So that we can keep records to their corresponding companies as the enrichment worklfow intends.

### Raw and Processed Data
In this system, the seperation of raw and processed data is critical. I use 2 seperate tables in this layer. First is the **Raw Enrichment Table**. In this table, I keep the actual-complete raw response that is obtained from providers like Apollo. It is also important to create a relation between enrichment call with a **run_id**. This way for every enrichment call, I can observe: 
- provider_name 
- requested_at 
- recieved_at
- response_payload 
- http_status 
- processing_status 
- mapping_version 
- validation_verison
via run_id. This way I gain advantage in terms of; data-loosage, replay, retention-compression policies. Even tough the response of the provider changes I guarante that there is no data loss since we keep the actual raw data and it also enables a replay option so that previous calls can be inspected and processed in order to backfill operations. Furthermore we can apply retention and compression policies to optimize the source usage and costs which enables to keep the data econamically without deleting it. Layer's this part brings huge advantage by not directly relating to the external provider schema. 

Second table would be **Curated/Enriched Business Table**. The design of this table is fully related to business-intent. Responses that came from the providers like Apollo, would not be directly written into this table. Columns like related to intention of the business, useful for segmentation or outbound cycles would selected. The data that came from the provider initially passed into validation and mapping layers. In these layer the following checks would be made: 
- Does the response includes required fields ? 
- Is the quality of the response okey ? 
- Are there any new fields that I am not aware of ? 
After these validations the data should be fine to write to curated table. This way we ensure business-intent table clear enough, stable enough and eligible to be used in analyzing workflows. 

It is also important to decide at the beginning whether we keep the most updated version or keeping the changes in time for the **Curated/Enriched Business Table**. If we only keep the updated versions, as the entities of the companies change in time, we loose the old information as we update the fields like worker count, revenue band, funding stage and so on. Therefore I decided to work with fields like valid_from, valid_to and is_current, so that I can see the both company's most up to date profile and track how it has changed in the past. This way is useful for trend analysis, monitoring and accurately processing historical data.

Validation and Schema Drift topics are important to ensure healthy system. For every response that came from any provider 2 things should be checked: does the response includes required fields, are there any new unknown fields ? If there is missing required field then the record status should be labeled as partial or failed_validation. If the new fields are appearing, instead of failing the pipeline creating events or alarms would be more suitable. In this system, the unknown new fields should be stored in a column called **new_detected_fields**. This way it would be much easier to capture the changes in the provider schema and if these new unknown fields keep arriving, migration to new curated table schema can be designed to backfill using the historical raw data. It is worth noticing to keep raw data; so that it enables historical data for a new column. 

### Identificaiton of useful areas for analytics and outbound
The seleciton of the fields is also made in business-intent way. Fields like industry, employee count range, revenue range, funding stage and etc. are important for analytics workflows. For the outbound fields like website, linkedin company url, hiring signals, growth signals should be useful. The key point is creating the curated table with business-intent way instead of provider response. So this layer should not be the copy of the provider schema, instead it should be designed in internal business model. 