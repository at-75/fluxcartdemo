## FluxCartAPI


-It's using Postgres hosted on Neon

-API is written in FastAPI and is deployed on render on this URI
```
https://fluxcartdemo.onrender.com/identify
```

You can make API calls like this 
```
curl --location 'https://fluxcartdemo.onrender.com/identify' \
--header 'Content-Type: application/json' \
--data-raw '{
"email": "test@gmail.com",
"phone": "1111111111"
}'
```
 
 This will be a sample response
```
{
    "contact": {
        "primaryContactId": 42,
        "emails": [
            "test@gmail.com"
        ],
        "phoneNumbers": [
            "1111111111"
        ],
        "secondaryContactIds": []
    }
}
```
