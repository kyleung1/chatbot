# Chat-KL1 API Documentation

Welcome to the API documentation for Chat-KL1. It is aimed to be a chatbot that answers questions about me. This was made using FastAPI, python, and Pymongo for mongodb.

[Click to view user interface](https://portfolio-v1-5-kappa.vercel.app/Chatbot)

## Base URL

The base URL for all API endpoints is: https://chatbot-api-31xm.onrender.com/

## Endpoints

### Getting all questions and answers

- **Method:** [GET]
- **Path:** `/`
- **Response:**
    - **Success:** [200]
    ```json
        [
            {
                "question": "who are you",
                "answer": "blah blah."
            },
            {
                "question": "how old are you",
                "answer": "10"
            }
        ]
    ```

### Getting a response

- **Method:** [POST]
- **Path:** `/`
- **Request Body:**
    ```
        {
            user_msg: str
            session: int | None = None
        }
    ```
- **Response:**
    - **Success:** [200]
    ```json
        {
            "answer": "blah blah.",
            "session": 1234
        }
    ```