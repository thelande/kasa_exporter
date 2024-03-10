IMAGE_NAME ?= kasa-exporter
IMAGE_TAG ?= v0.2.0

.DEFAULT_GOAL := help

##@ General

.PHONY: help
help: ## Show this help message.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Building

.PHONY: nerdctl-build
nerdctl-build:  ## Build the container image using nerdctl
	nerdctl -n k8s.io build -t $(IMAGE_NAME):$(IMAGE_TAG) .

.PHONY: docker-build
docker-build:  ## Build the container image using docker
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

.PHONY: podman-build
podman-build:  ## Build the container image using podman
	podman build -t $(IMAGE_NAME):$(IMAGE_TAG) .

##@ Deployment

.PHONY: deploy
deploy:  ## Deploy the container as a kubernetes deployment and service
	kubectl apply -f deploy/manifests

.PHONY: undeploy
undeploy:  ## Remove the kubernetes deployment and service
	kubectl delete -f deploy/manifests
