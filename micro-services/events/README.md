# Events Microservice

Microservicio en Flask para gestionar competencias, eventos y rutas de ciclismo.

## Endpoints

- `GET /health`
- `POST|GET|PUT|DELETE /api/v1/events/competitions`
- `POST|GET|PUT|DELETE /api/v1/events/events`
- `POST|GET|PUT|DELETE /api/v1/events/routes`

## Autenticacion

La API usa Bearer tokens emitidos por Firebase Authentication:

- `Authorization: Bearer <firebase_id_token>`


El microservicio valida el token con Firebase Admin SDK usando variables de entorno cargadas desde `.env`.

## Levantar con Docker

```bash
docker compose up --build
```

Servicios definidos en `docker-compose.yml`:

- `events-api`: API Flask en `http://localhost:5000`
- `db`: MySQL 8.4 en `localhost:3306`
- `events-adminer`: Adminer en `http://localhost:8080`
- `events-tests`: runner de pruebas con perfil `test`

## Variables de entorno

- `DATABASE_URL`
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

Configuracion actual relevante:

- `DATABASE_URL` usa el host interno `db`
- Firebase apunta al proyecto `bikes-36e5a`

## Ver la base de datos

Abre `http://localhost:8080` y entra con:

- System: `MySQL`
- Server: `db`
- Username: ``
- Password: ``
- Database: `events_db`

## Pruebas

```bash
pytest
```

Para correrlas en Docker:

```bash
docker compose --profile test up --build events-tests
```
