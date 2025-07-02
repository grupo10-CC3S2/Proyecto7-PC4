REPO = "https://github.com/grupo10-CC3S2/Proyecto7-PC4"

build-image:
	docker build -t timeserver:v3 app

setup-minikube:
	minikube start --container-runtime=docker
	minikube kubectl cluster-info
	minikube kubectl -- apply -f k8s/
	minikube kubectl get pods
	minikube dashboard

clear-minikube:
	minikube stop
	minikube delete

setup:
	kubectl cluster-info
	kubectl apply -f k8s/
	kubectl get pods

clear:
	kubectl delete all --all --namespace=default --force --grace-period=0

teardown:
	flux suspend kustomization kustomization-github
	kubectl delete namespace flux-system
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
	kubectl get pods -n default -o custom-columns=POD:.metadata.name,IMAGE:.spec.containers[*].image