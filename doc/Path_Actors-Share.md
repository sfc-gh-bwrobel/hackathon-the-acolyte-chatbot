# Share Actors

## Create a Secure View

```sql
CREATE OR REPLACE SECURE VIEW SV_ALL_ACTORS_CLEAN
AS
SELECT
    CONCAT(
    actor || ' has played the role of ' || movie_character,
    '\n\n\nHistory of the engagement: \n' || history
    ) as listing_text
FROM ACOLYTE_DB.ACTORS.V_ALL_ACTORS_CLEAN
;
```

## Create a Listing

Share with your team mate from the same region

1. Go to `Data products` – `Provider Studio` – click `+ listing`.

1. provide the title of the listing:
`The Acolyte – actors and history of their engagement`

1. Click Next.

1. In `What's in the listing?` select `SV_ALL_ACTORS_CLEAN`.

1. For the `Secure Share Identifier` type `ACOLYTE_ACTORS`.

1. In `Briefly describe your listing` provide a meaningful description
   of the content of the listing, like
   `This is a cool listing containing all the information regarding actors of the The Acolyte series.`

1. Click `Save draft`.

1. Click `Preview` to see how the listing is going to look like.

1. `Exit Preview` to edit the listing.

1. Scroll to the bottom of the page and fill the rest of the `Optional Information`.

1. Scroll to the bottom of the page and fill the rest of the `Optional Information`.
   Especially important is a query that can be used to feed the Corstex Search service.
   Please provide the query, and give it appropriate description so that consumers can
   directly use it.

1. Once done, click `Preview` to confirm how your listing looks like.

1. Ask your partner for their `Account Identifier` and add
them as a `Consumer account`.

1. `Save` - `Publish listing` - `Done`.

## Get data regarding the Episodes

Go to `Data Products` - `Private Sharing` and find the listing
shared with you. Click it and explore.
Once you are sure you want to use it, click `Get`.

Expand `Options` and put `ACOLYTE_DB_EPISODES` as database name.
Click `Get`.

Run example queries shared by the data provider.

> **Note**, that you should have received an example query
> you can use for your Cortex Search service. If the query
> is not there, ask your data provider for one.

---

Next step: [discuss with full data set](Path_Actors-Full_Chat.md)