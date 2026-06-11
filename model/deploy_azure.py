"""
deploy_azure.py
---------------
Despliega el modelo XGBoost en Azure AI Foundry (Azure ML)
como un Managed Online Endpoint.

Pasos:
  1. Conecta con el workspace de Azure ML
  2. Registra el modelo en el Model Registry
  3. Crea (o actualiza) un Managed Online Endpoint
  4. Despliega el modelo con las dependencias necesarias
  5. Activa el 100% del tráfico a la nueva versión

Requisitos previos:
  - az login  (Azure CLI autenticado)
  - Variables de entorno en .env configuradas

Uso:
    python model/deploy_azure.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    ManagedOnlineEndpoint,
    ManagedOnlineDeployment,
    Model,
    Environment,
    CodeConfiguration,
)
from azure.ai.ml.constants import AssetTypes
from azure.identity import DefaultAzureCredential

load_dotenv()

# ─── Configuración ───────────────────────────────────────────────────────────
SUBSCRIPTION_ID  = os.getenv("AZURE_SUBSCRIPTION_ID")
RESOURCE_GROUP   = os.getenv("AZURE_RESOURCE_GROUP")
WORKSPACE_NAME   = os.getenv("AZURE_ML_WORKSPACE")
ENDPOINT_NAME    = os.getenv("AZURE_ML_ENDPOINT_NAME", "football-predictor-endpoint")
DEPLOYMENT_NAME  = os.getenv("AZURE_ML_DEPLOYMENT_NAME", "xgboost-v1")

MODEL_DIR = Path(__file__).parent
ARTIFACTS_DIR = MODEL_DIR / "artifacts"


def get_ml_client() -> MLClient:
    """Conecta con Azure ML usando DefaultAzureCredential (az login)."""
    credential = DefaultAzureCredential()
    client = MLClient(
        credential=credential,
        subscription_id=SUBSCRIPTION_ID,
        resource_group_name=RESOURCE_GROUP,
        workspace_name=WORKSPACE_NAME,
    )
    print(f"✅  Conectado a workspace: {WORKSPACE_NAME}")
    return client


def register_model(client: MLClient) -> Model:
    """Registra el modelo en el Azure ML Model Registry."""
    print("\n📦  Registrando modelo en Azure ML Model Registry...")

    model = Model(
        path=str(ARTIFACTS_DIR),
        name="football-xgboost-predictor",
        description="XGBoost model for football match outcome prediction",
        type=AssetTypes.CUSTOM_MODEL,
    )

    registered = client.models.create_or_update(model)
    print(f"    Modelo registrado: {registered.name} v{registered.version}")
    return registered


def create_or_update_endpoint(client: MLClient) -> ManagedOnlineEndpoint:
    """Crea el Managed Online Endpoint si no existe."""
    print(f"\n🌐  Configurando endpoint: {ENDPOINT_NAME}...")

    endpoint = ManagedOnlineEndpoint(
        name=ENDPOINT_NAME,
        description="Football match predictor endpoint",
        auth_mode="key",
        tags={"project": "football-predictor", "framework": "xgboost"},
    )

    created = client.online_endpoints.begin_create_or_update(endpoint).result()
    print(f"    Endpoint listo: {created.scoring_uri}")
    return created


def deploy_model(client: MLClient, registered_model: Model) -> ManagedOnlineDeployment:
    """Crea el deployment con el modelo y sus dependencias."""
    print(f"\n🚀  Desplegando modelo como '{DEPLOYMENT_NAME}'...")

    # Entorno con las dependencias necesarias
    env = Environment(
        name="football-predictor-env",
        description="Environment for football predictor",
        conda_file=str(MODEL_DIR / "conda.yml"),
        image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest",
    )

    deployment = ManagedOnlineDeployment(
        name=DEPLOYMENT_NAME,
        endpoint_name=ENDPOINT_NAME,
        model=registered_model,
        environment=env,
        code_configuration=CodeConfiguration(
            code=str(MODEL_DIR),
            scoring_script="score.py",
        ),
        instance_type="Standard_DS2_v2",
        instance_count=1,
    )

    result = client.online_deployments.begin_create_or_update(deployment).result()
    print(f"    Deployment completado: {result.name}")
    return result


def set_traffic(client: MLClient):
    """Dirige el 100% del tráfico a la nueva versión."""
    print(f"\n🔀  Configurando tráfico → 100% a '{DEPLOYMENT_NAME}'...")

    endpoint = client.online_endpoints.get(name=ENDPOINT_NAME)
    endpoint.traffic = {DEPLOYMENT_NAME: 100}
    client.online_endpoints.begin_create_or_update(endpoint).result()
    print("    Tráfico configurado correctamente.")


def print_summary(client: MLClient):
    """Muestra el resumen del endpoint desplegado."""
    endpoint = client.online_endpoints.get(name=ENDPOINT_NAME)
    keys = client.online_endpoints.get_keys(name=ENDPOINT_NAME)

    print("\n" + "=" * 60)
    print("  RESUMEN DEL DESPLIEGUE")
    print("=" * 60)
    print(f"  Endpoint URL : {endpoint.scoring_uri}")
    print(f"  API Key      : {keys.primary_key[:20]}...")
    print()
    print("  Añade estas variables a tu .env:")
    print(f"  AZURE_ML_ENDPOINT_URL={endpoint.scoring_uri}")
    print(f"  AZURE_ML_API_KEY={keys.primary_key}")
    print("=" * 60)


def main():
    print("=" * 60)
    print("  FOOTBALL PREDICTOR — Despliegue en Azure AI Foundry")
    print("=" * 60)

    if not all([SUBSCRIPTION_ID, RESOURCE_GROUP, WORKSPACE_NAME]):
        print("❌  Faltan variables de entorno. Revisa tu fichero .env")
        sys.exit(1)

    client = get_ml_client()
    model  = register_model(client)
    create_or_update_endpoint(client)
    deploy_model(client, model)
    set_traffic(client)
    print_summary(client)

    print("\n✅  Despliegue completado. Siguiente paso:")
    print("    uvicorn backend.main:app --reload")


if __name__ == "__main__":
    main()
