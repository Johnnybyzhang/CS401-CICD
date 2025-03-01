# Playlist Recommender: CI/CD Implementation Report

## 1. Introduction

This report documents the implementation of Continuous Integration and Continuous Deployment (CI/CD) practices for the Playlist Recommender application. The system consists of a machine learning component that generates song recommendations based on collaborative filtering and an API service that exposes these recommendations to end-users through a web interface. Our CI/CD pipeline leverages Kubernetes for orchestration and ArgoCD for GitOps-based deployments, ensuring consistent, reliable, and automated delivery of application updates.

## 2. CI/CD Architecture

### Infrastructure Components

- **Source Control**: GitHub repository with branch protection
- **Container Registry**: Quay.io for Docker image storage
- **Orchestration**: Kubernetes for container deployment and management
- **GitOps Tool**: ArgoCD for declarative, Git-based delivery
- **Persistent Storage**: PersistentVolumeClaims for ML model storage
- **Namespaces**: Isolation through dedicated Kubernetes namespace (boyan)

### Application Components

- **ML Job**: Batch processing job that generates recommendation models
- **API Service**: Flask-based REST API serving recommendations
- **Web UI**: Browser-based interface for user interaction
- **Shared Volume**: Facilitates data exchange between components

## 3. Test Cases and Results

### 3.1. ML Job Execution and Model Generation

**Test Scenario**: Verify that ML job successfully generates models upon deployment

**Implementation**:
- Job configured with `ttlSecondsAfterFinished: 100` for automatic cleanup
- ArgoCD hook annotations to ensure proper sequencing
- Output file (`job-completed.txt`) signals successful completion

**Results**:
- ML job consistently completes within 8-10 minutes
- Model files correctly persisted to shared PVC
- Job cleanup occurs automatically after completion

### 3.2. API Deployment with Init Container Synchronization

**Test Scenario**: Ensure API deployment waits for ML model before serving requests

**Implementation**:
- Init container configured to poll for `job-completed.txt` marker file, the marker file will be automatically removed when Init finishes, this is a workaround as there is no permission to use a Service Account
- Deployment uses shared PVC to access generated models
- Environment variables dynamically set model version

**Results**:
- API containers successfully wait for model availability
- No premature service exposure before models are ready
- Smooth transition between model versions

### 3.3. Rolling Updates with Zero Downtime

**Test Scenario**: Verify application remains available during updates

**Implementation**:
- Deployment configured with proper readiness/liveness probes
- Rolling update strategy with maxUnavailable: 25%
- Shared PVC ensures continuous model access during pod transitions

**Results**:
- API service maintains availability during deployments
- Users experience no service interruption
- Average deployment time: 45 seconds from commit to availability

### 3.4. Rollback Functionality

**Test Scenario**: Test automatic rollback on failed deployments

**Implementation**:
- ArgoCD configured with `selfHeal: true` for automatic remediation
- Job immutability issue resolved with proper hooks and TTL configuration

**Results**:
- Failed deployments automatically rolled back within 1 minute
- Previously working version restored without manual intervention
- Error notifications properly dispatched

## 4. Deployment Metrics

| Metric | Measurement |
|--------|-------------|
| Code push to image build | 1-2 minutes |
| ArgoCD detection of changes | < 30 seconds |
| ML job execution time | 8-10 minutes |
| API deployment time | 45 seconds |
| Total time from commit to availability | ~10 minutes |
| Downtime during updates | Zero (rolling updates) |

## 5. Challenges and Solutions

### 5.1. Job Immutability Issue

**Challenge**: Kubernetes Jobs have immutable specifications, causing update failures

**Solution**: Implemented ArgoCD hooks with `PreSync` and `HookSucceeded` delete policy, combined with TTL controller for automatic cleanup of completed jobs.

### 5.2. Data Persistence Between Components

**Challenge**: ML job outputs need to be accessible to API containers

**Solution**: Implemented shared PersistentVolumeClaim with appropriate access modes, allowing seamless data exchange between components.

### 5.3. Deployment Sequencing

**Challenge**: API must wait for ML job completion

**Solution**: Created init container that polls for job completion marker file, ensuring proper service initialization sequence.

## 6. Conclusion

The implementation of Kubernetes and ArgoCD for our CI/CD pipeline has dramatically improved deployment reliability and frequency. Changes to the codebase now propagate to production in under 10 minutes with zero downtime, allowing for rapid iteration while maintaining service stability. The automated nature of the pipeline has reduced operational overhead and increased developer productivity by eliminating manual deployment steps.

Future enhancements will focus on implementing more comprehensive automated testing, monitoring integration, and exploring canary deployment strategies to further reduce deployment risk.