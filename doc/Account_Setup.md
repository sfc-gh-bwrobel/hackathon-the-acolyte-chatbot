# Account Setup

We will be building a chatbot to answer a few questions
regarding The Acolyte, a Star Wars franchise by Disey.

## Create free Snowflake account

Create a new account in one of the regions supporting LLMs you want to work with.
They can be found [here](https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions#availability).

At the moment of writing one of those would do:

* AWS US West 2 (Oregon)
* AWS US East 1 (N. Virginia)
* AWS Europe Central 1 (Frankfurt)
* AWS Europe West 1 (Ireland)

## Setup your database

Login to Snowflake, and create a new worksheet. Use role `ACCOUNTADMIN`.

```sql
USE ROLE ACCOUNTADMIN;
CREATE OR REPLACE DATABASE ACOLYTE_DB;
CREATE OR REPLACE WAREHOUSE ACOLYTE_WH WITH WAREHOUSE_SIZE='xsmall';
CREATE OR REPLACE SCHEMA ACOLYTE_DB.CHATS;
CREATE OR REPLACE SCHEMA ACOLYTE_DB.SERVICES;
```
