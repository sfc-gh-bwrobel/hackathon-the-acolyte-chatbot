# Simple Chat

> **Note**: For all the examples of Streamlit app make sure
> to add `snowflake.core` package if it is missing. To do
> so click source code and `Packages` menu on the top.
> Search for the missing package and add it. Reboot the
> application afterwards.


> **Note 2**: Store all your streamlit applications
> in `CHATS` schema.

## Streamlit Application

1. Create new Streamlit application. Call it: `Simple Chat`.
1. Use created resources for `App location` and `App warehouse`.
1. Copy and paste the code from `streamlit/simple_chat.py`

## Questions to ask

Ask sample questions, like:

1. What is Java, in 2 sentences?
1. What is Golang, in 2 sentences?
1. Compare them shortly.

Your chat will not be able to answer the last quesiton, as it
does not remember any context.

> **Note**: In the Options, change model used by the chat
> and compare the answers.

---

Next step: extend the chat with [history](Simple_Chat_with_History.md)
