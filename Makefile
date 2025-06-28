REPO = "https://github.com/grupo10-CC3S2/Proyecto7-PC4"

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
	flux suspend kustomization kustomization-github
	kubectl delete all --all --namespace=default --force --grace-period=0
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

flux-suspend:
	flux suspend kustomization kustomization-github

pod-images:
	kubectl get pods --namespace=default -o json | jq '.items[].spec.containers[] | {pod: .name, container_name: .name, image: .image}'