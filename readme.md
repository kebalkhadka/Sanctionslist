# SanctionWatch Project README

## Overview

SanctionWatch is a classroom project simulating a real-world ETL pipeline to consolidate global sanctions data from multiple official sources into a MySQL database. This README documents the data sources, assumptions, sample SQL queries, and instructions for restoring the database dump.

## Data Sources Used

The following Nine sanctions sources were used to extract data:

1. **United Nations Security Council Consolidated List**
   - Format: XML
   - Description: Contains individuals and entities subject to UN sanctions.
2. **US OFAC Specially Designated Nationals (SDN) List**
   - Format: XML
   - Description: Lists individuals and entities with blocked assets under US jurisdiction.
3. **European Union Consolidated Financial Sanctions List**
   - Format: XML
   - Description: Includes persons, groups, and entities under EU sanctions.
4. **UK HMT Sanctions List**
   - Format: XML
   - Description: UK’s consolidated sanctions list for financial restrictions.
5. **US OFAC - Consolidated**

   - Format: xml(data scrapped using selenium base)
   - Description: US consolidated data for sanction list .

6. **Australia DFAT**
   - Format: csv
   - Description: conatins data realted to australia.
7. **Switzerland SECO**

   - Format: xml
   - Description: contains data related to swiss.

8. **Cannada**

- Format: xml
- Description: contains data relatd to swiss.

9. **Interpol Red Notices**

- Format: CSV
- Description: contains interpol's data here this data is obtained though webscraping using selenium base

## Assumptions Made While Transforming Data

1. **Unified Schema Mapping**:

   - Fields like `name`, `nationality`, and `sanction_type` were mapped from source-specific fields (e.g., UN’s `FULL_NAME` to `name`). If a field was missing, it was set to NULL or “Unknown” (e.g., `alias` in some records).

2. **Schema Variations Across Data Sources**

- Out of the nine data sources used, seven shared a similar schema, which included fields like name, alias, nationality, designation
  sanction_type, and source. These records were unified and loaded into the primary table sanctioned_entities, with references to normalized tables such as aliases, nationalities, etc.(UN,uk,USOFAC-consolidated, USOFAC-SDN switzerland, eur,australia DFAT)

- The remaining two sources had different schemas, so they were processed separately and loaded into dedicated tables tailored to their unique structures.(cannada,interpol)

3. **Duplicate Handling**:

   - Entities appearing in multiple sources (e.g., same individual in UN and OFAC) were assigned unique `entity_id` values unless clear evidence (e.g., identical names and nationalities) indicated they were the same entity.

4. **Handling Ambiguous or Multi-Valued Fields**:

   - Assumed that fields with multiple values (e.g., multiple nationalities in EU sanctions) would be split into separate rows in the nationalities table, prioritizing normalization over storing comma-separated values in a single field.

5. **Missing Data Handling**:

   - For UK’s `designation` column (54% missing), a linear logistic model was trained on non-missing data using features from `name` (TF-IDF encoded) and `additional_info` (text features). Predicted values were used to fill missing entries. Acurracy of 69% was obtained.

## Sample Sql query for browsing the dataset

Sanction database contains six tables :
`sanctioned_entities`,`aliases`,`nationalities` and `sanction_types` these table stores the data for 7 diff sources as they share same schema.
here sanctioned_entities is the primary tables and other and reference table
`cannada_tbl` stores the data related to sources cannda.
`interpol_tbl` and `interpol_nationality` store the data related to interpol red notices here `interpol_tbl` is the main table and `interpol_nationality` is the reference table.

Below are the sample query to explore the data:

1. **List all the sanctioned_entities from specific source**:
   ```sql
   SELECT *
   FROM sanctioned_entities
   WHERE source = 'UN'
   LIMIT 20;
   ```
2. **Find entities with a specific nationality**:

   ```sql
   SELECT e.entity_id, e.name, n.nationality
   FROM sanctioned_entities e
   JOIN nationalities n ON e.entity_id = n.entity_id
   WHERE n.nationality = 'Pakistan';
   ```

3. **Retrieve aliases for a specific entity**:

   ```sql
   SELECT e.name, a.alias_name
   FROM sanctioned_entities e
   JOIN aliases a ON e.entity_id = a.entity_id
   WHERE e.name LIKE '%Zafar%';

   ```

4. **Find Entities with Specific Designations:**

   ```sql
   SELECT entity_id, name, designation, source
   FROM sanctioned_entities
   WHERE source = 'UN' AND designation = 'Individual'
   LIMIT 10;

   ```

5. **Count entities by source**:
   ```sql
   SELECT source, COUNT(*) AS entity_count
   FROM sanctioned_entities
   GROUP BY source;
   ```
6. **Identify Entities with Multiple Nationalities:Finds entities with more than one nationality**
   ```sql
   SELECT e.entity_id, e.name, COUNT(n.nat_id) AS nationality_count
   FROM sanctioned_entities e
   JOIN nationalities n ON e.entity_id = n.entity_id
   GROUP BY e.entity_id, e.name
   HAVING nationality_count > 1
   LIMIT 5;
   ```
7. ** Identify name of person whose name were recoded in sanction list 1 year ago
   Cannada_tbl(name,nationalities,date_of_listing,source)**
   ```sql
   select name from cannada_tbl where YEAR(current_date()) - year(date_of_listing) = 1;
   ```
8. **Interpol_table**
   **_ interpol_tbl(name,age) and interpol_nationality(nationality,nat_id)_**
   **_Get all people and their nationalities_**

   ```sql
   SELECT t.name, t.age, n.nationality
   FROM interpol_tbl t
   JOIN interpol_nationality n ON t.entity_id = n.entity_id;

   ```

9. **_Count how many people belong to each nationality_**
   ```sql
   SELECT n.nationality, COUNT(*) AS total_people
   FROM interpol_nationality n
   GROUP BY n.nationality;
   ```

## Instructions to Restore the .sql Dump

To restore the `sanctionwatch.sql` database dump to a MySQL instance, follow these steps:

1. **Ensure MySQL is Installed**:

   - Verify MySQL Server is running on your system.

2. **Create a New Schema**

   - Open MySQL Workbench or use the command line to create a new schema
   - eg: restored_sanctions

3. **Edit the SQL Dump File**

   - Edit the mysql dump file
     - Find the line
     ```sql
     USE sanctions;
     ```
     - Replace it with
     ```sql
     USE restored_sanctions;
     ```
   - Save the file

4. **Go to server**

   - Click on Data import
   - Click on Import from self contained file and provide the path
   - Click import

5. **Verify Tables**

   - Open MySQL Workbench.
   - Go to the restored_sanctions schema.
   - Click "Refresh" to view imported tables.
