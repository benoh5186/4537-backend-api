# API Documentation
Manages API calls to AI API, Security, Authorization, and Database


#Set Up
1. Start virtual environment
```bash
python -m venv .venv
```
2. Activate virtual environment (always before running)
macOS/Linux:
```bash
source .venv/bin/activate
```
Windows:
```bash
.venv\Scripts\activate
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
4. Run app
```bash
uvicorn main:app --reload
```


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


## Schemas
- **UserCreate** – inserted row for `user` table with constraints for email, password, and is_admin  
- **UserLogin** – validated login input  
- **Email** – validated email update  
- **Password** – validated password update  

Validation errors in any schema raise **422**.

## Database
Database class manages CRUD for the `user`, `api_usage`, and `api_request_stats` tables.

## Exceptions
- **PasswordException** – incorrect password  
- **ValidationException** – schema violations  
- **HTTPException** – general authorization or data errors  



# Endpoints

# AUTH ROUTES (`AuthRouter`)

## POST: '/api/v1/auth/login'
Authenticates the user if their credential matches one of the rows in the `user` table in the database.
- `email` parameter: string that needs to match email format specified in UserLogin schema.
- `password` parameter: string that represents unhashed password to compare to the hashed password stored in the database.
    - needs to be encoded in bytes before checking using bcrypt.checkpw(login_pass_in_bytes, user_database_pw_in_bytes)
- Returns Ok(200) if the user is authenticated with cookie that includes jwt.
- Returns Unprocessable Entity(422) if the login information does not match UserLogin schema.
- Returns Unauthorized(401) when the email exists in the database, but the password does not match the stored hash.

### Request Example

##### Successful Request
- Req.body:
```json
{
    "email" : "hookaDoncic@lakers.com",
    "password" : "thisisrealluka"
}
```
- Res:
```json
{
    "code" : 200,
    "message" : "login success"
}
```

##### `password` does not match the hashed password for the same email
- Req.body:
```json
{
    "email" : "austinReaves@lakers.com",
    "password" : "bestWhiteBoyInTheLeague"
}
```
- Res:
```json
{
    "code" : 400
}
```

##### Invalid credentials: email does not exist in the database
- Req.body:
```json
{
    "email" : "viniJrBallonDor@soccer.com",
    "password" : "lmao67420"
}
```
- Res:
```json
{
    "code" : 401
}
```

##### Invalid `email` format
- Req.body:
```json
{
    "email" : "luka",
    "password" : "lukalakeRs"
}
```
- Res:
```json
{
    "code" : 422,
    "detail" : { "email" : false, "password" : true }
}
```

##### Invalid `password` length
- Req.body:
```json
{
    "email" : "marcus@brazil.com",
    "password" : "lages"
}
```
- Res:
```json
{
    "code" : 422,
    "detail" : { "email" : true, "password" : false }
}
```

##### Invalid `email` and `password`
- Req.body:
```json
{
    "email" : "ethan@korea.com",
    "password" : "park"
}
```
- Res:
```json
{
    "code" : 422,
    "detail" : { "email" : false, "password" : false }
}
```

---

## POST: '/api/v1/auth/signup'
Inserts user information such as email, password, and is_admin that represent a new row in the `user` table.
- `email` parameter: must match email format specified in UserCreate schema.
- `password` parameter: must match password rules in UserCreate schema.
    - must be encoded in bytes before hashing with bcrypt.
- `is_admin` parameter: boolean that specifies if the user is an admin.
- Returns Created(201) if the user is successfully inserted.
- Returns Unprocessable Entity(422) if the input does not match UserCreate schema.
- Returns Conflict(409) if the email already exists.

### Request Example

##### Successful Request
- Req.body:
```json
{
    "email" : "hookaDoncic@lakers.com",
    "password" : "thisisrealluka",
    "is_admin" : false
}
```
- Res:
```json
{
    "code" : 201,
    "message" : "sign up successful"
}
```

##### Email already exists
- Req.body:
```json
{
    "email" : "rodriBallonDor@soccer.com",
    "password" : "lmao67420"
}
```
- Res:
```json
{
    "code" : 409
}
```

##### Invalid `email`
```json
{
    "email" : "luka",
    "password" : "lukalakeRs"
}
```
- Res:
```json
{
    "code" : 422,
    "detail" : { "email" : false, "password" : true }
}
```

##### Invalid `password`
```json
{
    "email" : "marcus@brazil.com",
    "password" : "lages"
}
```
- Res:
```json
{
    "code" : 422,
    "detail" : { "email" : true, "password" : false }
}
```

---

## GET: '/api/v1/auth/authenticate'
Checks if the browser is currently in session by validating JWT in the cookie.
- Returns Ok(200) if JWT is valid.
- Returns Unauthorized(401) if JWT does not exist or has expired.
- Returns additional user information: `is_admin`, `api_usage`, and `email`.

##### If JWT is active:
```json
{
    "code": 200,
    "is_admin": false,
    "api_usage": 14,
    "email": "user@gmail.com"
}
```

##### If JWT is missing or expired:
```json
{
    "code" : 401,
    "message" : "unauthorized"
}
```

---

# PROFILE ROUTES (`ProfileRouter`)

## PATCH: '/api/v1/user/password'
Updates the password for the authenticated user.
- Valid JWT required.
- Body validated using Password schema.
- Returns Conflict(409) if the new password matches the old password (bcrypt comparison).
- Returns Unauthorized(401) if JWT is missing.
- Returns Unprocessable Entity(422) if schema validation fails.

### Request Example

##### Successful Request
```json
{ "password" : "newPassword123" }
```
- Res:
```json
{ "message" : "password change success" }
```

##### Same password as before
- Res:
```json
{ "code" : 409 }
```

##### Invalid password format
```json
{ "code" : 422 }
```

---

## PATCH: '/api/v1/user/email'
Updates the email for the authenticated user.
- Valid JWT required.
- Body validated using Email schema.
- Returns Conflict(409) if the new email is identical to the current one.
- Returns Conflict(409) if changing fails because email already exists.
- Returns Unprocessable Entity(422) if schema validation fails.

### Request Example

##### Successful Request
```json
{ "email" : "newEmail@gmail.com" }
```
- Res:
```json
{
    "message" : "email change success",
    "new_email" : "newEmail@gmail.com"
}
```

##### Same email
```json
{ "detail" : { "same_email" : true } }
```

##### Email already exists
```json
{ "detail" : { "same_email" : false } }
```

---

# AI ROUTES (`AI`)

## POST: '/api/v1/service/ai/text'
Sends text to AI backend for JSON parsing.
- Increments API usage.
- Returns parsed JSON and updated api_usage.
- Returns Unauthorized(401) if JWT missing.

### Request Example
```json
{
  "text": "hello world",
  "lang": "en"
}
```
- Res:
```json
{
  "data": {"greetings" : "hello"},
  "api_usage": 12
}
```

---

## POST: '/api/v1/service/ai/schema'
Sends text + schema to AI backend for structured parsing.
- Same behavior as text endpoint.
- Returns parsed data and updated api_usage.

### Request Example
```json
{
  "text": "hello world",
  "lang": "en",
  "schema": {"greetings" : "hello" }
}
```
- Res:
```json
{
  "data": {"greetings" : "hello"  },
  "api_usage": 11
}
```

---

# ADMIN ROUTES (`Admin`)

## GET: '/api/v1/admin/users'
Retrieves all users along with their usage counts.
- Requires admin privileges.
- Returns Forbidden(403) if user is not an admin.

### Response Example
```json
[
  {
    "uid": 1,
    "email": "ben@gmail.com",
    "is_admin": false,
    "remaining_usage": 12
  }
]
```

---

## DELETE: '/api/v1/admin/user/{uid}'
Deletes a user from the system.
- Requires admin privileges.
- Returns No Content(204) on success.
- Returns Not Found(404) if user does not exist.

---

## GET: '/api/v1/admin/endpoints'
Returns list of all API calls tracked in endpoint logs.
- Requires admin privileges.

### Response Example
```json
[
  {
    "http_method": "GET",
    "endpoint": "/api/v1/auth/authenticate",
    "request_count": 15
  }
]
```