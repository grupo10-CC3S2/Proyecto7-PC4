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