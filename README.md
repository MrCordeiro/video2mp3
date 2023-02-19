# Video to MP# converter

## Introduction

This repository refers to the [freeCodeCamp.org](https://www.freecodecamp.org/) hands-on tutorial from Kantan Coding about microservices architecture and distributed systems using Python, Kubernetes, RabbitMQ, MongoDB, and MySQL. Watch the original [YouTube video](https://www.youtube.com/watch?v=hmkF77F9TLw) for more information.

I don't trust Oracle, so I replaced MySQL with PostgreSQL. :)

## Prerequisites

Make sure you have the following installed on your machine:

- [Docker](https://www.docker.com/)
- [`kubectl`](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [minikube](https://minikube.sigs.k8s.io/docs/start/)
- [k9s](https://k9scli.io/topics/install/)
- [Python 3+](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/)

If you are running the app locally for the first time, there are a few more steps to take:

### Create fake users

We assume users already exist in a database somewhere. For this demo, can will create a minimal database with a single table and a one user.

The fixture for creating the table initial user is in `auth\init.sql`.

PowerShell:

```powershell
Get-Content auth\init.sql | psql -U <YOUR-USERNAME> -p <PORT-NUMBER>
```

### Start minikube

```bash
minikube start
```

### Enable MiniKube addons

```bash
minikube addons enable ingress
```

## Running the app locally

Start by applying all the Kubernetes manifests for the many services and create the appropriate resources:

```bash
kubectl apply -f auth/manifests/
kubectl apply -f gateway/manifests/
```

Finally, tunnel the services to your local machine:

```bash
minikube tunnel
```

## Commands

After adding a new service, push the image to Docker Hub:

```bash
docker build -t <YOUR-USERNAME>/<SERVICE-NAME> .
docker tag <YOUR-USERNAME>/<SERVICE-NAME> <YOUR-USERNAME>/<SERVICE-NAME>:latest
docker push <YOUR-USERNAME>/<SERVICE-NAME>:latest
```

To scale a service, run:

```bash
kubectl scale deployment --replicas=<NUMBER-OF-REPLICAS> <SERVICE-NAME> 
```

You might want to scale some services that are not in use to 0 replicas to save resources.
