"""
deploy_azure.py
---------------
Deploys the XGBoost model on Azure AI Foundry (Azure ML)
as a Managed Online Endpoint.

Steps:
  1. Connect to Azure ML workspace
  2. Register the model in the Model Registry
  3. Create (or update) a Managed Online Endpoint
  4. Deploy the model with required dependencies
  5. Route 100% of traffic to the new version

Prerequisites:
  - az login (Azure CLI authenticated)
  - Environment variables set in .env

Usage:
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
    """Connects to Azure ML using DefaultAzureCredential (az login)."""
    credential = DefaultAzureCredential()
    client = MLClient(
        credential=credential,
        subscription_id=SUBSCRIPTION_ID,
        resource_group_name=RESOURCE_GROUP,
        workspace_name=WORKSPACE_NAME,
    )
    print(f"✅  Connected to workspace: {WORKSPACE_NAME}")
    return client


def register_model(client: MLClient) -> Model:
    """Registers the model in the Azure ML Model Registry."""
    print("\n📦  Registering model in Azure ML Model Registry...")

    model = Model(
        path=str(ARTIFACTS_DIR),
        name="football-xgboost-predictor",
        description="XGBoost model for football match outcome prediction",
        type=AssetTypes.CUSTOM_MODEL,
    )

    registered = client.models.create_or_update(model)
    print(f"    Model registered: {registered.name} v{registered.version}")
    return registered


def create_or_update_endpoint(client: MLClient) -> ManagedOnlineEndpoint:
    """Creates the Managed Online Endpoint if it does not exist."""
    print(f"\n🌐  Configuring endpoint: {ENDPOINT_NAME}...")

    endpoint = ManagedOnlineEndpoint(
        name=ENDPOINT_NAME,
        description="Football match predictor endpoint",
        auth_mode="key",
        tags={"project": "football-predictor", "framework": "xgboost"},
    )

    created = client.online_endpoints.begin_create_or_update(endpoint).result()
    print(f"    Endpoint ready: {created.scoring_uri}")
    return created


def deploy_model(client: MLClient, registered_model: Model) -> ManagedOnlineDeployment:
    """Creates the deployment with the model and its dependencies."""
    print(f"\n🚀  Deploying model as '{DEPLOYMENT_NAME}'...")

    # Environment with the necessary dependencies
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
    print(f"    Deployment completed: {result.name}")
    return result


def set_traffic(client: MLClient):
    """Routes 100% of the traffic to the new version."""
    print(f"\n🔀  Configuring traffic → 100% to '{DEPLOYMENT_NAME}'...")

    endpoint = client.online_endpoints.get(name=ENDPOINT_NAME)
    endpoint.traffic = {DEPLOYMENT_NAME: 100}
    client.online_endpoints.begin_create_or_update(endpoint).result()
    print("    Traffic routed successfully.")


def print_summary(client: MLClient):
    """Displays a summary of the deployed endpoint."""
    endpoint = client.online_endpoints.get(name=ENDPOINT_NAME)
    keys = client.online_endpoints.get_keys(name=ENDPOINT_NAME)

    print("\n" + "=" * 60)
    print("  DEPLOYMENT SUMMARY")
    print("=" * 60)
    print(f"  Endpoint URL : {endpoint.scoring_uri}")
    print(f"  API Key      : {keys.primary_key[:20]}...")
    print()
    print("  Add these variables to your .env:")
    print(f"  AZURE_ML_ENDPOINT_URL={endpoint.scoring_uri}")
    print(f"  AZURE_ML_API_KEY={keys.primary_key}")
    print("=" * 60)


def main():
    print("=" * 60)
    print("  FOOTBALL PREDICTOR — Deployment on Azure AI Foundry")
    print("=" * 60)

    if not all([SUBSCRIPTION_ID, RESOURCE_GROUP, WORKSPACE_NAME]):
        print("❌  Missing environment variables. Check your .env file")
        sys.exit(1)

    client = get_ml_client()
    model  = register_model(client)
    create_or_update_endpoint(client)
    deploy_model(client, model)
    set_traffic(client)
    print_summary(client)

    print("\n✅  Deployment completed. Next step:")
    print("    uvicorn backend.main:app --reload")


if __name__ == "__main__":
    main()
