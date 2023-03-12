# Video to MP3 converter

## Introduction

This repository refers to the [freeCodeCamp.org](https://www.freecodecamp.org/) hands-on tutorial from Kantan Coding about microservices architecture and distributed systems using Python, Kubernetes, RabbitMQ, MongoDB, and MySQL. Watch the original [YouTube video](https://www.youtube.com/watch?v=hmkF77F9TLw) for more information.

I don't trust Oracle, so I replaced MySQL with PostgreSQL. :)

## Prerequisites

Make sure you have the following installed on your machine:

- [Docker](https://www.docker.com/)
- [`kubectl`](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [minikube](https://minikube.sigs.k8s.io/docs/start/)
- [MongoDB](https://www.mongodb.com/try/download/community)
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

After starting `minikube`, don't forget to applying all the Kubernetes manifests so that you can create the appropriate resources for each service:

```bash
kubectl apply -f auth/manifests/
kubectl apply -f gateway/manifests/
kubectl apply -f rabbit/manifests/
```

Edit your `/etc/hosts` file and add the following lines:

```hosts
127.0.0.1 kubernetes.docker.internal
127.0.0.1 mp3converter.com
127.0.0.1 rabbitmq-manager.com
```

Finally, tunnel the services to your local machine:

```bash
minikube tunnel
```

### Create the RabbitMQ queue

Open the RabbitMQ management console at [http://rabbitmq-manager.com:15672](http://rabbitmq-manager.com:15672) and create the following queues:

- `video`, with Durability set to `Durable`
- `mp3`, also with Durability set to `Durable`

> **Note**: The default user and password for the RabbitMQ management console is `guest` and `guest`.

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

## Usage

Start by logging in with the your credentials. We will be using the fake user we created [earlier](#create-fake-users).

```bash
curl -X POST http://mp3converter.com/login -u test@email.com:fake_pwd
```

Collect the token from the response and use it to convert a video to MP3:

```bash
curl -X POST -F 'filename=@<FILE_PATH.mp4>' -H 'Authorization: Bearer <TOKEN>' http://mp3converter.com/upload
```

The converter should send a notification to the email you used for your fake user. After that, to download the converted file, run:

```bash
curl -X GET --output <OUTPUT_PATH.mp3> -H "Authorization: Bearer <TOKEN>" "http://mp3converter.com/download?fid=<FID_FROM_NOTIFICATION>"
```
