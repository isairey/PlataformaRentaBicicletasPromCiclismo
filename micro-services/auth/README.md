# Auth Microservice

Microservicio en Flask para autenticacion de usuarios con Firebase Authentication.

## Endpoints

- `GET /health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`

## Configuracion

El servicio carga su configuracion desde el archivo `.env` y construye las credenciales de Firebase Admin SDK directamente desde variables de entorno.

Variables principales:

- `FLASK_APP=app.py`
- `FLASK_RUN_PORT=5000`
- `FIREBASE_WEB_API_KEY`
- `FIREBASE_TYPE`
- `FIREBASE_PROJECT_ID`
- `FIREBASE_PRIVATE_KEY_ID`
- `FIREBASE_PRIVATE_KEY`
- `FIREBASE_CLIENT_EMAIL`
- `FIREBASE_CLIENT_ID`
- `FIREBASE_AUTH_URI`
- `FIREBASE_TOKEN_URI`
- `FIREBASE_AUTH_PROVIDER_X509_CERT_URL`
- `FIREBASE_CLIENT_X509_CERT_URL`
- `FIREBASE_UNIVERSE_DOMAIN`

Importante:

- El archivo `.env` contiene secretos y esta ignorado por Git.
- Firebase se configura desde variables de entorno.

## Levantar con Docker

```bash
docker compose up --build
```

Servicios definidos en `docker-compose.yml`:

- `auth-api`: API Flask en `http://localhost:5001`
- `auth-tests`: runner de pruebas con perfil `test`

## Ejecutar pruebas

Para correr los tests dentro de Docker:

```bash
docker compose --profile test up --build auth-tests
```

Si prefieres correrlos localmente:

```bash
pytest tests -v
```

## Notas

- `register` crea el usuario en Firebase y asigna claims personalizados como `role` y `admin`.
- `login` usa la API REST de Firebase Authentication y retorna `idToken` y `refreshToken`.
- `logout` revoca los refresh tokens del usuario autenticado.
- El contenedor expone el puerto `5000` internamente y se publica como `5001` en la maquina host.
