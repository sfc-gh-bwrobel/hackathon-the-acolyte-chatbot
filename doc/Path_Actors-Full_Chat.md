# Build full chat

Explore the concatenated data:

```sql
SELECT listing_text FROM ACOLYTE_DB_EPISODES.EPISODES.SV_ALL_EPISODES_CLEAN
UNION ALL
SELECT listing_text FROM ACOLYTE_DB.ACTORS.SV_ALL_ACTORS_CLEAN
```

Create a dynamic table to automatically refresh on new data:

```sql
CREATE OR REPLACE DYNAMIC TABLE ACOLYTE_DB.ACTORS.ALL_ACOLYTE_INFORMATION
 TARGET_LAG = DOWNSTREAM
  WAREHOUSE = ACOLYTE_WH
  AS
SELECT listing_text FROM ACOLYTE_DB_EPISODES.EPISODES.SV_ALL_EPISODES_CLEAN
UNION ALL
SELECT listing_text FROM ACOLYTE_DB.ACTORS.SV_ALL_ACTORS_CLEAN
;
```

Build a service that works with the data:

```sql
CREATE OR REPLACE CORTEX SEARCH SERVICE ACOLYTE_DB.SERVICES.ALL_ACOLYTE_INFORMATION_SVC
ON listing_text
WAREHOUSE = ACOLYTE_WH
TARGET_LAG = '5 minutes'
AS
SELECT listing_text FROM ACOLYTE_DB.ACTORS.ALL_ACOLYTE_INFORMATION
```

## Chat with the data

Using `Simple The Acolyte Chat with RAG` chat with your data:

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

## Done

Thank you for folliwing the whole path!
