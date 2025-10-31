# API Documentation
Manages API calls to AI API, Security, Authorization, and Database


#Set Up
1. 





# Headers
- `Content-Type: application/json`
- Allow all origins(for now)
- authentication required with JWT



# HTTP Status Codes

- **200**: Successful Request
- **201**: Created
- **400**: Bad Request 
- **401**: Unauthorized
- **409**: Conflict 
- **422**: Unprocessable Entity


# Schemas 
- UserCreation: represents a row to be inserted in `user` table in the mysql database with defined constraints for all parameters such as email, password, is_admin. ValidationException will be raised if the parameters in the body of the request does not match the parameter constraints defined in the schema.
- UserLogin: represents a row to fetch from user table in the database, with defined constraints for all parameters such as email and password. ValidationException is raised if the constraints are not met.


# Database
A class with methods that executes queries for `user` table in mysql database. Creates `user` table if it does not already exist in the database.


# Exceptions
- PasswordException: Raised if the email is found in the database, but the password from the request body does not match the password for the row with the identical email in the database


#Endpoints

## POST: 'api/auth/login'
Authenticates the user if their credential matches one of the rows in the `user` table in the database.
- `email` parameter: string that needs to match type, EmailType, from pydantic
= `password` parameter: string that represents unhashed password to compare to the hashed password in the database
    -  needs to be encoded in bytes before checking if the password for the user email, if found in the database, matches it using bcrypt.checkpw(login_pass_in_bytes, user_database_pw_in_bytes) method
- Returns Ok(200), if the user is authenticated with cookie that includes jwt
- Returns Unprocessable Entity(422), if the login information does not match UserLogin 
Schema 
- Returns Unauthorized(401) when the email exists in the database, but the password does not match the password in the row with the same email in the database.

### Request Example

##### Successful Request
- Req.body:
``` json
{
    "email" : "hookaDoncic@lakers.com",
    "password" : "thisisrealluka"
}

- Res:
```json
{
    "code" : 200,
    "message" : "login success"
}
```

##### `password` does not match the password for the row in `user` table with the same email
- Req.body:
``` json
{
    "email" : "austinReaves@lakers.com",
    "password" : "bestWhiteBoyInTheLeague"
}
```
- Res:
``` json 
{
    "code" : 400,
}
```

##### Invalid credentials: if `email` does not exist in the database
- Req.body:
``` json
{
    "email" : "viniJrBallonDor@soccer.com",
    "password" :"lmao67420"
}
```
- Res:
``` json
{
    "code" : 401
}
```

##### Invalid `email`(not matching format specified in UserLogin schema)
- Req.body:
``` json
{ 
    "email" : "luka",
    "password" : "lukalakeRs"
}
```
- Res:
``` json
{
    "code" : 422,
    "detail" : {
        "email" : False,
        "password" : True
    }
}
```

##### Invalid `password`(not matching length specified in UserLogin schema)
- Req.body:
``` json
{
    "email" : "marcus@brazil.com",
    "password" : "lages"
}
```

- Res:
``` json
{
    "code" : 422,
    "detail" : {
        "email" : True,
        "password" : False
    }
}
```

##### Invalid `email` and `password`
- Req.body:
``` json 
{
    "email" : "ethan@korea.com",
    "password" : "park"
}
```
- Res:
``` json
{
    "code" : 422,
    "detail" : {
        "email" : False,
        "password" : False
    }
}
```

## POST: 'api/auth/signup'
Inserts user information such as email, password, and is_admin that represents a row in the user table into the database
- `email` parameter: string that needs to match email format specified in UserLogin schema
- `password` parameter: string that needs to match password format specified in UserLogin schema
    -  needs to be encoded in bytes before hashing it with bcrypt
- `is_admin` parameter: bool that specifies if the user signing up is an admin
- Returns Created(201), if the user information is successfully inserted into the database
- Returns Unprocessable Entity(422) if the user information does not match UserCreation 
Schema 
- Returns Conflict(409) if the user email already exists in the database

### Request Example

##### Successful Request
- Req.body:
``` json
{
    "email" : "hookaDoncic@lakers.com",
    "password" : "thisisrealluka",
    "is_admin" : "False"
}

- Res:
```json
{
    "code" : 201,
    "message" : "sign up successful"
}
```

##### Invalid credentials: if `email` exists in the database
- Req.body:
``` json
{
    "email" : "rodriBallonDor@soccer.com",
    "password" :"lmao67420"
}
```
- Res:
``` json
{
    "code" : 409
}
```

##### Invalid `email`(not matching format specified in UserLogin schema)
- Req.body:
``` json
{ 
    "email" : "luka",
    "password" : "lukalakeRs"
}
```
- Res:
``` json
{
    "code" : 422,
    "detail" : {
        "email" : False,
        "password" : True
    }
}
```

##### Invalid `password`(not matching length specified in UserLogin schema)
- Req.body:
``` json
{
    "email" : "marcus@brazil.com",
    "password" : "lages"
}
```

- Res:
``` json
{
    "code" : 422,
    "detail" : {
        "email" : True,
        "password" : False
    }
}
```

##### Invalid `email` and `password`
- Req.body:
``` json 
{
    "email" : "ethan@korea.com",
    "password" : "park"
}
```
- Res:
``` json
{
    "code" : 422,
    "detail" : {
        "email" : False,
        "password" : False
    }
}
```

## GET: 'api/auth/session'
Checks if the browser is currently in session by checking if the JWT inside the cookie is not expired yet.
- Returns Ok(200), if the JWT is still active
- Returns Unauthorized(401) if the JWT does not exist or has expired 

### Request Example

##### If JWT is active
- Res:
```json
{
    "code" : 200,
    "message" : "In session"
}
```

##### If JWT does not exist or has expired

- Res:
``` json
{
    "code" : 401,
    "message" : "not in session"
}
```
