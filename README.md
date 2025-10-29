# 4537-backend-api


#API Endpoints

###
POST: 'v1/login/'
- Authenticates the user if user credential matches the the credential in the database.
Example:
- Req: v1/login
    - request.body: 
        {
            "email" : "lukaDoncic@lakers.com",
            "password" : "austinReaves"
        }
    - return data(response):
        - return { "message" : "Login successful"}
        - raise HTTPEXCEPTION(
            status_code = 400,
            detail = "user already signed in"
        )


###
POST: 'v1/signup/'
- Adds user credentials to the database and authenticates if the credential does not yet exist in the database.
Example:
- Req: v1/signup
    - request.body:
        {
            "email" : "hookaDoncic@lakers.com",
            "password" : "viniciusjrisbad"
        }
    - return data(response):
        - return {"message" : "signup successful"}
        - response.set_cookie(
        key="jwt",
        value=the_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=60
    )


    