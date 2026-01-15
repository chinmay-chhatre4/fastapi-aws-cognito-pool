# FastAPI Cognito Auth Service

Minimal FastAPI service integrating with AWS Cognito for registration, confirmation, sign-in, password reset, change password and sign-out.

This README provides a concise, ordered set of steps to run the app locally, where to find the automatic API docs (Swagger), and which environment variables are mandatory before starting the service.

**Prerequisites**
- **Python**: 3.10+ recommended.
- **AWS account**: required to configure Cognito user pool and client.
- **Git / local clone**: repository is assumed cloned.

**Mandatory environment variables**
Before running the application you must set the following environment variables (they are required by the app and have no defaults):

- `AWS_REGION` — AWS region of your Cognito resources (e.g., `us-east-1`).
- `COGNITO_USER_POOL_ID` — Cognito User Pool ID.
- `COGNITO_CLIENT_ID` — Cognito App Client ID.

**Optional environment variables**
- `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` — only needed if the app will make AWS SDK calls requiring credentials locally.
- `COGNITO_CLIENT_SECRET` — only if your Cognito App Client has a secret.
- `JWKS_URL` — custom JWKS URL; if unset the app will derive JWKS from Cognito metadata.
- `LOG_LEVEL` — logging level (default: `INFO`).
- `ENV` — environment name (default: `development`).
- `PORT` — port to run the app (default: `8000`).

Tip: The project loads environment variables from a `.env` file at the repository root if present. Create a `.env` file with the mandatory variables before running.

Example `.env` (replace placeholders):

```
AWS_REGION=us-east-1
COGNITO_USER_POOL_ID=us-east-1_ExamplePoolId
COGNITO_CLIENT_ID=exampleclientid123456789
# Optional
AWS_ACCESS_KEY_ID=YOUR_AWS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET
COGNITO_CLIENT_SECRET=your_client_secret
JWKS_URL=https://cognito-idp.us-east-1.amazonaws.com/us-east-1_ExamplePoolId/.well-known/jwks.json
LOG_LEVEL=INFO
ENV=development
PORT=8000
```

**Run locally (recommended)**
1. Create and activate a virtual environment (Windows):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

2. Install dependencies using the `uv` package manager (recommended):

```powershell
# Install uv per https://docs.astral.sh/uv/getting-started/installation/
curl -sSfL https://install.astral.sh | sh
# Install project dependencies from pyproject.toml/uv.lock
uv install --yes
```

3. Ensure your `.env` contains the mandatory variables from above.

4. Run the app with uvicorn:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

By default the app listens on the port defined by `PORT` (default `8000`).

**Swagger / API docs & useful endpoints**

After starting the server locally, you can explore and test endpoints using the built-in API docs:

- Swagger UI: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json
- Health check: http://localhost:8000/health

Auth endpoints are mounted under `/api/v1/auth` (see FastAPI docs UI to view available operations and request/response schemas).

**Notes**
- The app uses AWS Cognito for authentication flows — ensure your Cognito User Pool and App Client are created and the IDs are set in your `.env`.
- If running in an environment where AWS credentials are required (for example, local AWS SDK calls), set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` or configure an AWS profile.
- A CloudFormation template is available at `infrastructure/cloudformation/template.yaml` for automating infrastructure setup.

Included files
- `.env.example` — sample environment file with required and optional keys.

**Run with Docker**
Build and run the included `Dockerfile` (ensure your `.env` or environment variables are set before running):

1. Build the image:

```powershell
docker build -t fastapi-cognito .
```

2. Run the container (bind port and provide env file):

```powershell
docker run --env-file .env -p 8000:8000 --rm fastapi-cognito
```

3. Verify the service at http://localhost:8000/docs

Note: The `Dockerfile` in this repository uses the project sources; mounting a local volume or building after installing dependencies may be useful for local development.