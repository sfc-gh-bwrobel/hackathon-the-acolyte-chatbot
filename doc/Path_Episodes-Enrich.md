# Enrich the Chatbot with Episode information

In this path you load data for the Episodes.

## Create a new schema

```sql
USE ROLE ACCOUNTADMIN;
USE DATABASE ACOLYTE_DB;
CREATE SCHEMA EPISODES;
USE SCHEMA EPISODES;
USE WAREHOUSE ACOLYTE_WH;
```

## Create new table from file

1. In Snowsight, go to `Data` -> `Databases` -> `ACOLYTE_DB` -> `EPISODES` and create a table from file (top right corner).
1. Upload `data/episodes/season_1-all_episodes.tsv` from git
1. Create table `ALL_EPISODES_RAW`
1. Click Next, Load.

> **Note**: The file is a tab-separated file, and contains a header.

Explore the data using worksheets:

```sql
SELECT * FROM ACOLYTE_DB.EPISODES.ALL_EPISODES_RAW;
```

## Clean the data

Clean the data ba bit:

```sql
SELECT
    NO,
    REPLACE(TITLE, '"', '') as TITLE,
    DIRECTED_BY,
    WRITTEN_BY,
    TO_DATE(ORIGINAL_RELEASE_DATE, 'MMMM DD, YYYY') as ORIGINAL_RELEASE_DATE,
    PLOT
FROM ACOLYTE_DB.EPISODES.ALL_EPISODES_RAW
;
```

Based on the above query create a view:

```sql
CREATE OR REPLACE VIEW ACOLYTE_DB.EPISODES.V_ALL_EPISODES_CLEAN
  AS
SELECT
    NO,
    REPLACE(TITLE, '"', '') as TITLE,
    DIRECTED_BY,
    WRITTEN_BY,
    TO_DATE(ORIGINAL_RELEASE_DATE, 'MMMM DD, YYYY') as ORIGINAL_RELEASE_DATE,
    PLOT
FROM ACOLYTE_DB.EPISODES.ALL_EPISODES_RAW
```

## Create a Cortex Search Service

> **Note**: We are skipping attributes to filtern on,
> as we will not be using them [docs](https://docs.snowflake.com/en/sql-reference/sql/create-cortex-search).

Concatenate all interesting fields in `listing_text`.

Why do we do it?

Create the service as below:

```sql
CREATE OR REPLACE CORTEX SEARCH SERVICE ACOLYTE_DB.SERVICES.ALL_EPISODES_SVC
ON listing_text
WAREHOUSE = ACOLYTE_WH
TARGET_LAG = '5 minutes'
AS
SELECT
    CONCAT(
        'The Acolyte, eposode ' || NO,
        ', directed by ' || DIRECTED_BY,
        ', written by ' || WRITTEN_BY,
        ', released on ' || ORIGINAL_RELEASE_DATE,
        '\n\n\nPlot: \n' || PLOT
    ) as listing_text
FROM ACOLYTE_DB.EPISODES.V_ALL_EPISODES_CLEAN
;
```

### Helpful query

To explore, clean, or when you want to start over,
you can use the following queries:

```sql
SHOW CORTEX SEARCH SHOW CORTEX SEARCH SERVICES IN SCHEMA ACOLYTE_DB.SERVICES;
DESCRIBE CORTEX SEARCH SERVICE ACOLYTE_DB.SERVICES.ALL_EPISODES_SVC;
DROP CORTEX SEARCH SERVICE ACOLYTE_DB.SERVICES.ALL_EPISODES_SVC;
```

## Streamlit Application

1. Create new Streamlit application. Call it: `Simple The Acolyte Chat with RAG`.

1. Use created resources for `App location` and `App warehouse`.

1. Copy and paste the code from: `streamlit/simple_the_acolyte_chat_with_rag.py`

## Ask some quesitons

How does the chatbot behave?

1. Who is Sol?
1. Which actor was playing Sol?
1. How did he die?
1. When was he killed?
1. Who is Torbin?
1. Who played Torbin?
1. Who is Yoda?
1. Does he appear in The Acolyte?
1. How does he appear in the Acolyte?
1. List all characters that were killed in The Acolyte.

Change models the chatbot is using, and check again!
Rebooting the app in between will allow you to better
compare.

---

Next step: [share and enrich](Path_Episodes-Share.md)
