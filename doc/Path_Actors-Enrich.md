# Enrich the Chatbot with Actor information

In this path you load data for the Actors.

## Create a new schema

```sql
USE ROLE ACCOUNTADMIN;
USE DATABASE ACOLYTE_DB;
CREATE SCHEMA ACTORS;
USE SCHEMA ACTORS;
USE WAREHOUSE ACOLYTE_WH;
```

## Create new table from file

Go to Data -> Databases -> ACOLYTE_DB -> ACTORS and create a table from file (top right corner).
Upload `data/actors/actors_and_characters.tsv`.
Create table `ALL_ACTORS_RAW`
Click Next, Load.

> **Note**: The file is a tab-separated file, and contains a header.

Explore the data using worksheets:

```sql
SELECT * FROM ACOLYTE_DB.ACTORS.ALL_ACTORS_RAW;
```

## Clean the data

Clean the data ba bit:

```sql
WITH s as (
    SELECT
    SPLIT(WHO, ' as ') as splitted,
    history FROM ACOLYTE_DB.ACTORS.ALL_ACTORS_RAW
)
SELECT
    splitted[0]::VARCHAR as actor,
    splitted[1]::VARCHAR as move_character,
    history
FROM S
;
```

Based on the above query create a view:

```sql
CREATE OR REPLACE VIEW ACOLYTE_DB.ACTORS.V_ALL_ACTORS_CLEAN
  AS
WITH s as (
    SELECT
    SPLIT(WHO, ' as ') as splitted,
    history FROM ACOLYTE_DB.ACTORS.ALL_ACTORS_RAW
)
SELECT
    splitted[0]::VARCHAR as actor,
    splitted[1]::VARCHAR as movie_character,
    history
FROM S;
```

## Create a Cortex Search Service

> **Note**: We are skipping attributes to filtern on,
> as we will not be using them [docs](https://docs.snowflake.com/en/sql-reference/sql/create-cortex-search).

Concatenate all interesting fields in `listing_text`.

Why do we do it?

Create the service as below:

```sql
CREATE OR REPLACE CORTEX SEARCH SERVICE ACOLYTE_DB.SERVICES.ALL_ACTORS_SVC
ON listing_text
WAREHOUSE = ACOLYTE_WH
TARGET_LAG = '5 minutes'
AS
SELECT
    CONCAT(
    actor || ' has played the role of ' || movie_character,
    '\n\n\nHistory of the engagement: \n' || history
    ) as listing_text
FROM ACOLYTE_DB.ACTORS.V_ALL_ACTORS_CLEAN
;
```

To clean, when you are ready:

```sql
SHOW CORTEX SEARCH SERVICES;
DESCRIBE CORTEX SEARCH SERVICE ACOLYTE_DB.EPISODES.ALL_ACTORS_SVC;
DROP CORTEX SEARCH SERVICE ACOLYTE_DB.EPISODES.ALL_ACTORS_SVC;
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
