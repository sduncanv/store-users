# store-users
Repositorio encargado de la gestión de **usuarios** en la aplicación principal.

Este repositorio maneja todo lo relacionado con usuarios: creación, lectura, actualización y eliminación de productos, también la autenticación y login. Forma parte de un ecosistema de microservicios junto a:

- [`store-products`](https://github.com/sduncanv/store-products)
- [`store-tools`](https://github.com/sduncanv/store-tools)

## 🧰 Tecnologías propias del repositorio

- cryptography


## Project Structure
```
.
├── Classes
│   ├── Users.py
│   ├── __init__.py
├── handlers
│   ├── UsersHandler.py
├── Models
│   ├── Users.py
│   ├── AuthenticatedUsers.py
│   ├── __init__.py
├── .env
├── .gitignore
├── locked-requirements.txt
├── pyproject.toml
├── README.md
├── script.py
├── serverless.yml
├── setup.py
```

## ⚙️ Setup and Installation

1. **Create and activate a virtual environment**
  ```sh
    python3 -m venv venv
    source venv/bin/activate
  ```

2. **Make sure you have your variables in .env with your credentials for: database, cloudinary**

3. **Create a requirements.txt**
  ```sh
    python3 script.py
  ```

4. **Install dependencies**
  ```sh
    pip install -r requirements.txt
  ```

5. **Run the application**
  ```sh
    serverless offline
  ```
The server will start and provide an IP address (e.g., `http://127.0.0.1:3003`).

## 🔌 Funciones

### 1. Create a user

**endpoint:** `POST /user`  
**description:** Crea un nuevo usuario.

#### Request body (JSON)

```json
{
    "username": "username",
    "password": "Password123",
    "email": "email@example.com"
}
```
#### Response
```json
{
    "statusCode": 200,
    "message": "Ok",
    "data": {
        "user_id": 1,
        "message": "User was created."
    }
}
```

### 2. Authenticate a user

**Endpoint:** `POST /authenticate_user`  
**Description:** Autentica un usuario en Cognito Aws.

#### Request body (JSON):

```json
{
    "username": "username",
    "code": "123456"
}
```
#### Response:
```json
{
    "statusCode": 200,
    "message": "Ok",
    "data": "User was confirmed."
}
```

### 3. Get a user or all user

**Endpoint:** `GET /user`  
**Description:** Obtiene los datos todos los usuarios, si se envía un parametro de ruta devuelve los datos de un usuario.

#### Params (Optionals):

```json
user_id: int
username: string
```
#### Response (JSON):
```json
{
    "statusCode": 200,
    "message": "Ok",
    "data": [
        {
            "user_id": 1,
            "name": "Name",
            "username": "username",
            "first_lastname": "lastname",
            "second_lastname": "lastname",
            "phone_number": "+570123456789",
            "email": "name@example.com",
            "type_document_id": 1,
            "document": 12345678,
            "city_id": 1,
            "active": 1,
            "created_at": "2025-04-15 17:04:47",
            "updated_at": "2025-04-15 17:04:47"
        }
    ]
}
```

### 4. Update a user

**Endpoint:** `PUT /user`  
**Description:** Update a user.

#### Request body (JSON):

```json
{
    "user_id": int,  // Required
    "name": "NewName",
    "first_lastname": "NewLastname"
}
```
#### Response:
```json
{
    "statusCode": 200,
    "message": "Ok",
    "data": "The user was updated."
}
```

### 5. Login

**Endpoint:** `POST /login`  
**Description:** Crea un nuevo usuario.

#### Request body (JSON)

```json
{
    "username": "username",
    "password": "password"
}
```
#### Response
```json
{
    "statusCode": 200,
    "message": "Ok",
    "data": {
        "AccessToken": "eyJraWQiOiJZMlJ3cW1EMnW7pPoAyLdAw",
        "ExpiresIn": 3600,
        "TokenType": "Bearer",
        "RefreshToken": "eyJjdHkiOiJKV1QiLCeSyGgcNwmrrYDnw",
        "IdToken": "eyJraWQiOiJnclk39DJ8KHz9pA"
    }
}
```