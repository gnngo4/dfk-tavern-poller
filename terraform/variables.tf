locals {
  data_lake_bucket = "data_lake"
}

variable "project" {
  description = "Your GCP Project ID"
}

variable "region" {
  description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
  default = "northamerica-northeast2"
  type = string
}

variable "storage_class" {
  description = "Storage class type for your bucket. Check official docs for more info."
  default = "STANDARD"
}

variable "BQ_DATASET" {
  description = "BigQuery Dataset"
  type = string
  default = "dfk_data"
}

variable "service_account" {
  description = "Service account to use for setting up GCP"
  type = string
  default = "gnvn-32@dfk-tavern.iam.gserviceaccount.com"
} 
