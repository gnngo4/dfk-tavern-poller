# Blockchain polling instance for DFK

## Project details
This project performs data ingestion for the NFT marketplace in [DefiKingdoms](https://defikingdoms.com/) (DFK) on the Harmony One blockchain. 
The idea is to use this tool to monitor and enable development of advanced analytics for their NFT marketplace. 

This project uses the Google Cloud platform (Google Cloud Storage and BigQuery).

Cloud infrastructure is managed with Terraform with the exception of Airflow and Kafka instances.

Data ingestion is carried out in two ways:
  1. An Airflow DAG is used to curate updated NFT hero statistics every 24 hours. This process uses 
  the DFK API to ingest relevant data into a Cloud Storage bucket (i.e., the data lake for this project). 
  The DAG ingests the data into the Cloud Storage as parquet files, and creates an external table in BigQuery 
  from all of the data.
  2. A Kafka stream processing platform is set-up to enable live-streaming and filtering of relevant blockchain 
  transactions. A Kafka producer feeds filtered transactions of the NFT marketplace from the blockchain to Kafka 
  consumers that will process each transaction, and the data is persisted in BigQuery.
  
## Reproduce this project

### Pre-requisites

The following requirements are needed to reproduce the project:
  1. A [Google Cloud Platform](https://cloud.google.com/) account.
  2. The [Google Cloud SDK](https://cloud.google.com/sdk). Instructions for installing it are below.

### Create a Google Cloud Project

1. Go to the [Google Cloud dashboard](https://console.cloud.google.com/home/dashboard) and create a new project.
2. Create a Service Account with the following roles:
   - `BigQuery Admin`
   - `Storage Admin`
   - `Storage Object Admin`
   - `Viewer`
3. Download the Service Account credentials file , rename it to `google_credentials.json` and store it in your home folder, in `$HOME/.google/credentials/`.
4. Activate the following APIs:
   - https://console.cloud.google.com/apis/library/iam.googleapis.com
   - https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com

### Create environment variable for credentials

Create an environment variable called `GOOGLE_APPLICATION_CREDENTIALS` and add it to `.bashrc`:
```
echo 'export GOOGLE_APPLICATION_CREDENTIALS="<path/to/google_credentials.json>" > ~/.bashrc'
source ~/.bashrc
```

### Set-up Google Cloud SDK

1. Download [Google Cloud SDK](https://cloud.google.com/sdk/docs/install).
2. Initialize by following instructions [here](https://cloud.google.com/sdk/docs/install-sdk).

### Create VM instance

```
gcloud compute instances create <vm-name> --zone=<google-cloud-zone> --image-family=ubuntu-2004-lts --image-project=ubuntu-os-cloud --machine-type=e2-standard-4 --boot-disk-size=40GB
```
> Change `vm-name` to name of your choice and `google-cloud-zone` to match your location.

### Set-up SSH access to the VM

Configure Google Cloud SDK to this project. `gcloud projects list` shows projects on your account. 
Change to this project with `gcloud config set project this-project`.
Set-up SSH access to the VM with `gcloud compute config-ssh`. 
Now you should be able to SSH into your VM with `ssh instance.zone.project`

### VM installations

Run `sudo apt update && sudo apt -y upgrade`

**Docker**
```
# Install
sudo apt install docker.io
# Give docker sudo permissions
sudo groupadd docker
sudo gpasswd -a $USER docker
# Re-login into the VM
sudo service docker restart
# Test to see if docker works
docker run hello-world
```
**Docker-compose**
```
# Choose version
URL=https://github.com/docker/compose/releases/download/v2.6.0/docker-compose-linux-x86_64
# Install steps
mkdir ~/bin
cd ~/bin
wget ${URL} -O docker-compose
chmod +x docker-compose
cd ~
echo 'export PATH="${HOME}/bin:${PATH}" > ~/.bashrc'
source ~/.bashrc
# Test
docker-compose version
```
**Terraform**
```
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install terraform
```
**Google credentials**
Add `google_credentials.json` to `$HOME/.google/credentials/` and set it as an environment variable.
```
echo 'export GOOGLE_APPLICATION_CREDENTIALS="<path/to/google_credentials.json>" > ~/.bashrc'
source ~/.bashrc
```
**Clone the repository**
```
git clone https://github.com/gnngo4/dfk-tavern-poller.git
```
