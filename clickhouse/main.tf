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

  env = [
    "CLICKHOUSE_USER=${var.clickhouse_user}",
    "CLICKHOUSE_PASSWORD=${var.clickhouse_password}"
  ]

  ports {
    internal = 9000
    external = var.native_port
  }

  ports {
    internal = 8123
    external = var.http_port
  }

  volumes {
    host_path      = abspath("${path.module}/data")
    container_path = "/var/lib/clickhouse"
  }

  restart = "unless-stopped"
}
