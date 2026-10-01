Settingup the environment.
    Explain how to setup the environment.
    Give steps for UV init the project
    give the installations required to be added to requirements.txt
        eg : langchain
langchain_community
langchain-openai
langchain-groq
python-dotenv
langchain-google-genai
(and others that may be required like open ai, pydantic, etc)
    how to install it.
    then explain how to get a model key
    from groq and add note that you can get keys from gemini too.
    add a note that open ai and anthropic would require payment. So not required for this lessons.

---
We will be building the exact code that is present in the github repo.
For this please follow the initial setup prerequsites :

    1. Create a new folder in your preferred location.
    2. open it in a terminal or vs code or any ide
    3. run uv init .
        (note if you do not have uv or python installed please go ahead and install these.I had python 3.11.9 and uv : 0.11.3 but even some different versions would not matter)(please add jupyter as dependency to be installed as well)
    4. create a file called requirements.txt
    5. paste the foll
        openai
        langchain
        langchain_community
        langchain-openai
        langchain-groq
        python-dotenv
        langchain-google-genai
        langgraph
        langsmith
        langchain_tavily
    6. uv add -r requirements.txt
    7. To verify things are working correctly create a file called hi.py. use this code
        import langchain

        print("Everything is working fine")
        print(langchain.__version__)
    8. run using uv run hi.py
    9. We are good.

For the first part :

create a folder with the following name
Part I Understanding the Basics

---

1. Connecting with an LLM. using Open ai, for groq and geminis libs.

    We have many properitary providers like OpenAI and Anthropic.
    Some providers also provide a limited free tire without any upfront payment.
    Of these, I have demonstrated 2 GROQ and Gemini.

    The code explains how we can make our very first LLM call.

    Note we are using the packages and the sdks provided by OpenAi and Gemini.
    (GROQ is fully compatible with open ai standards so we can comfortably use the open ai apis for the same.)

    Under the hood, it is a rest call. authenticated and authorized by the apikey.


2. Changing the model. becomes an issue

    Say you have made you application using OpenAi standards.
    But they have not increased the pricing or changed a privacy policy that is now against your company's standards(privacy is a myth >_<)
    This would mean a big undertaking.
    I have demoed a simple change. But in reality the changes would be significant and a multi sprint dev cycle would be required.
    (dont give me the crap that we will be build following best practices and seperation of concerns, Yeah right like the newbies, vibees in your team have ever read the boar book!)




--
4. Open source vs properiatery model.

While we are here,
We can also download an open source model host it and make calls to it free!!!.
(well nothing is really free though)
So do it after this course. do not divert.