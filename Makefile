REPO = "https://github.com/grupo10-CC3S2/test-repo-pc4"

setup-v1:
	docker build -t timeserver:v1 app
	kubectl cluster-info
	kubectl apply -f k8s/
	kubectl get pods

setup-v2:
	docker build -t timeserver:v2 app
	kubectl apply -f k8s/
	kubectl get pods

teardown:
	kubectl delete -f k8s/
	docker image rm timeserver:v1
	docker image rm timeserver:v2

# GitOps

flux-init:
	flux check --pre
	flux install

flux-creater:
	flux create source git repo-github --url=$(REPO) --branch=main --interval=30s --export > ./flux-gitrepository.yaml
	kubectl apply -f ./flux-gitrepository.yaml

flux-createk:
	flux create kustomization kustomization-github --source=GitRepository/repo-github --path="./k8s" --prune=true --interval=30s --export > ./flux-kustomization.yaml
	kubectl apply -f ./flux-kustomization.yaml

flux-getk:
	flux get kustomizations

flux-watchk:
	flux get kustomizations --watch

pod-images:
	kubectl get pods -n default -l pod=timeserver-pod -o jsonpath='{.items[*].spec.containers[*].image}'