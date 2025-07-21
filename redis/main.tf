terraform {
  required_version = ">= 1.4"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

resource "docker_image" "this" {
  name = var.image
}

resource "docker_container" "this" {
  name  = var.container_name
  image = docker_image.this.image_id

  command = ["redis-server", "--appendonly", "yes"]

  ports {
    internal = 6379
    external = var.port
  }

  volumes {
    host_path      = abspath("${path.module}/data")
    container_path = "/data"
  }

  restart = "unless-stopped"
}