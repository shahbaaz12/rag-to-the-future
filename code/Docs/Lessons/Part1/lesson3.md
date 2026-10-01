1. Langchain.

        Well lang chain is..
        it is the entityframework to you ado.net
        it is the spring(java specific) to your jdbc
        it is the TypeORM to your node.

        well not really I just went with the flow.

        it is a convenient set of tools that you can use to connect to an LLM and do much more.
        It is provider agnostic and
        Most importantly it can work with any LLM provider with the same code.


2. Connecting with an LLM using Langchain.
        Do you see the init_chat_model


3. Invoking Various models.
        changing the model is now easy and the same set of code works with almost any model

4. Temperatures

        temperature is a parameter that controls the randomness of a language model's output. It affects
how creative or deterministic the responses are.

. Lower values (0.0 - 0.3) - More deterministic and predictable.
. Higher values (0.7 - 1.5) - More random, creative, and diverse.

Use Case Recommended Temperature

Factual answers (math, code, facts) 0.0 - 0.3

Balanced response (general QA, explanations) 0.5 - 0.7

Creative writing, storytelling, jokes 0.9 - 1.2

Maximum randomness (wild ideas, brainstorming) 1.5+


5. max tokens.
