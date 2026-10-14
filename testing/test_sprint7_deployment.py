import os
import sys
import yaml

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_sprint7_deployment_configs():
    print("\n==================================================")
    print("RUNNING SPRINT 7 DEPLOYMENT SCHEMA INTEGRATION TEST")
    print("==================================================")

    # 1. Parse Dockerfile
    print("[Step 1] Parsing Dockerfile syntax...")
    dockerfile_path = "Dockerfile"
    assert os.path.exists(dockerfile_path), "Error: Dockerfile not found."
    with open(dockerfile_path, "r") as f:
        content = f.read()
        assert "FROM" in content, "Error: Dockerfile is missing a base image FROM instruction."
    print("Dockerfile syntax validated successfully.")

    # 2. Parse k8s/deployment.yaml
    print("\n[Step 2] Validating Kubernetes Deployment YAML structure...")
    deployment_path = "k8s/deployment.yaml"
    assert os.path.exists(deployment_path), "Error: deployment.yaml not found."
    with open(deployment_path, "r") as f:
        deployment_data = yaml.safe_load(f)
        assert deployment_data["apiVersion"] == "apps/v1", "Error: deployment.yaml invalid apiVersion."
        assert deployment_data["kind"] == "Deployment", "Error: deployment.yaml invalid resource kind."
        assert deployment_data["metadata"]["name"] == "agentx-api", "Error: deployment.yaml invalid metadata name."
    print("deployment.yaml parsed successfully.")

    # 3. Parse k8s/hpa.yaml
    print("\n[Step 3] Validating Kubernetes Horizontal Pod Autoscaler YAML structure...")
    hpa_path = "k8s/hpa.yaml"
    assert os.path.exists(hpa_path), "Error: hpa.yaml not found."
    with open(hpa_path, "r") as f:
        hpa_data = yaml.safe_load(f)
        assert "autoscaling" in hpa_data["apiVersion"], "Error: hpa.yaml invalid apiVersion."
        assert hpa_data["kind"] == "HorizontalPodAutoscaler", "Error: hpa.yaml invalid resource kind."
        assert hpa_data["spec"]["minReplicas"] == 2, "Error: hpa.yaml invalid minReplicas."
    print("hpa.yaml parsed successfully.")

    # 4. Parse .github/workflows/ci.yml
    print("\n[Step 4] Validating GitHub Actions CI workflow YAML structure...")
    ci_path = ".github/workflows/ci.yml"
    assert os.path.exists(ci_path), "Error: ci.yml not found."
    with open(ci_path, "r") as f:
        ci_data = yaml.safe_load(f)
        assert ci_data["name"] == "AgentX CI Pipeline", "Error: ci.yml invalid workflow name."
        assert "build-and-test" in ci_data["jobs"], "Error: ci.yml invalid jobs list."
    print("ci.yml parsed successfully.")

    print("\n==================================================")
    print("SPRINT 7 INTEGRATION TEST: ALL TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    test_sprint7_deployment_configs()
