"""Terraform Infrastructure as Code auto-generator.

Generates Terraform HCL configurations for deploying the application
to cloud providers (AWS, GCP, Azure).
"""

from __future__ import annotations

from typing import Any


class TerraformGenerator:
    """Generates Terraform IaC files from architecture descriptions."""

    def generate(
        self,
        architecture: dict[str, Any],
        project_name: str = "",
        provider: str = "aws",
    ) -> dict[str, str]:
        """Generate Terraform files from architecture."""
        name = project_name or "app"
        safe_name = name.replace("-", "_")
        components = architecture.get("components", [])
        tech = architecture.get("tech_stack", {})
        databases = tech.get("databases", [])

        files: dict[str, str] = {}
        files["terraform/main.tf"] = self._generate_main(safe_name, provider)
        files["terraform/variables.tf"] = self._generate_variables(safe_name)
        files["terraform/outputs.tf"] = self._generate_outputs(safe_name)

        has_services = any(c.get("type") == "service" for c in components)
        if has_services:
            files["terraform/ecs.tf"] = self._generate_ecs(safe_name)

        if databases:
            files["terraform/rds.tf"] = self._generate_rds(safe_name)

        files["terraform/networking.tf"] = self._generate_networking(safe_name)
        files["terraform/terraform.tfvars.example"] = self._generate_tfvars(safe_name)

        return files

    @staticmethod
    def _generate_main(name: str, provider: str) -> str:
        return (
            f"# {name} infrastructure\n\n"
            "terraform {\n"
            '  required_version = ">= 1.5.0"\n\n'
            "  required_providers {\n"
            "    aws = {\n"
            '      source  = "hashicorp/aws"\n'
            '      version = "~> 5.0"\n'
            "    }\n"
            "  }\n\n"
            '  backend "s3" {\n'
            f'    bucket = "{name}-terraform-state"\n'
            f'    key    = "{name}/terraform.tfstate"\n'
            '    region = "us-east-1"\n'
            "  }\n"
            "}\n\n"
            'provider "aws" {\n'
            "  region = var.aws_region\n\n"
            "  default_tags {\n"
            "    tags = {\n"
            f'      Project     = "{name}"\n'
            "      Environment = var.environment\n"
            '      ManagedBy   = "terraform"\n'
            "    }\n"
            "  }\n"
            "}\n"
        )

    @staticmethod
    def _generate_variables(name: str) -> str:
        return (
            f"# Variables for {name}\n\n"
            'variable "aws_region" {\n'
            '  description = "AWS region"\n'
            "  type        = string\n"
            '  default     = "us-east-1"\n'
            "}\n\n"
            'variable "environment" {\n'
            '  description = "Environment name"\n'
            "  type        = string\n"
            '  default     = "production"\n'
            "}\n\n"
            'variable "app_name" {\n'
            '  description = "Application name"\n'
            "  type        = string\n"
            f'  default     = "{name}"\n'
            "}\n\n"
            'variable "container_port" {\n'
            '  description = "Container port"\n'
            "  type        = number\n"
            "  default     = 8000\n"
            "}\n\n"
            'variable "db_instance_class" {\n'
            '  description = "RDS instance class"\n'
            "  type        = string\n"
            '  default     = "db.t3.micro"\n'
            "}\n"
        )

    @staticmethod
    def _generate_outputs(name: str) -> str:
        return (
            f"# Outputs for {name}\n\n"
            'output "alb_dns" {\n'
            '  description = "ALB DNS name"\n'
            "  value       = aws_lb.main.dns_name\n"
            "}\n\n"
            'output "ecs_cluster" {\n'
            '  description = "ECS cluster name"\n'
            "  value       = aws_ecs_cluster.main.name\n"
            "}\n\n"
            'output "ecr_repository" {\n'
            '  description = "ECR repository URL"\n'
            "  value       = aws_ecr_repository.app.repository_url\n"
            "}\n"
        )

    @staticmethod
    def _generate_ecs(name: str) -> str:
        return (
            f"# ECS resources for {name}\n\n"
            'resource "aws_ecs_cluster" "main" {\n'
            f'  name = "${{var.app_name}}-${{var.environment}}"\n\n'
            "  setting {\n"
            '    name  = "containerInsights"\n'
            '    value = "enabled"\n'
            "  }\n"
            "}\n\n"
            'resource "aws_ecr_repository" "app" {\n'
            f"  name                 = var.app_name\n"
            '  image_tag_mutability = "MUTABLE"\n\n'
            "  image_scanning_configuration {\n"
            "    scan_on_push = true\n"
            "  }\n"
            "}\n\n"
            'resource "aws_ecs_task_definition" "app" {\n'
            f'  family                   = "${{var.app_name}}-task"\n'
            '  network_mode             = "awsvpc"\n'
            '  requires_compatibilities = ["FARGATE"]\n'
            "  cpu                      = 256\n"
            "  memory                   = 512\n\n"
            "  container_definitions = jsonencode([{\n"
            "    name  = var.app_name\n"
            '    image = "${aws_ecr_repository.app.repository_url}:latest"\n'
            "    portMappings = [{\n"
            "      containerPort = var.container_port\n"
            '      protocol      = "tcp"\n'
            "    }]\n"
            "    logConfiguration = {\n"
            '      logDriver = "awslogs"\n'
            "      options = {\n"
            f'        "awslogs-group"         = "/ecs/${{var.app_name}}"\n'
            '        "awslogs-region"        = var.aws_region\n'
            '        "awslogs-stream-prefix" = "ecs"\n'
            "      }\n"
            "    }\n"
            "  }])\n"
            "}\n\n"
            'resource "aws_ecs_service" "app" {\n'
            f'  name            = "${{var.app_name}}-service"\n'
            "  cluster         = aws_ecs_cluster.main.id\n"
            "  task_definition = aws_ecs_task_definition.app.arn\n"
            "  desired_count   = 2\n"
            '  launch_type     = "FARGATE"\n\n'
            "  network_configuration {\n"
            "    subnets         = aws_subnet.private[*].id\n"
            "    security_groups = [aws_security_group.ecs.id]\n"
            "  }\n\n"
            "  load_balancer {\n"
            "    target_group_arn = aws_lb_target_group.app.arn\n"
            "    container_name  = var.app_name\n"
            "    container_port  = var.container_port\n"
            "  }\n"
            "}\n"
        )

    @staticmethod
    def _generate_rds(name: str) -> str:
        return (
            f"# RDS resources for {name}\n\n"
            'resource "aws_db_instance" "main" {\n'
            f'  identifier     = "${{var.app_name}}-db"\n'
            '  engine         = "postgres"\n'
            '  engine_version = "16.1"\n'
            "  instance_class = var.db_instance_class\n\n"
            "  allocated_storage     = 20\n"
            "  max_allocated_storage = 100\n"
            "  storage_encrypted     = true\n\n"
            f'  db_name  = "{name}"\n'
            '  username = "app_user"\n'
            "  manage_master_user_password = true\n\n"
            "  vpc_security_group_ids = [aws_security_group.rds.id]\n"
            "  db_subnet_group_name   = aws_db_subnet_group.main.name\n\n"
            "  backup_retention_period = 7\n"
            "  skip_final_snapshot     = false\n"
            f'  final_snapshot_identifier = "${{var.app_name}}-final"\n'
            "}\n\n"
            'resource "aws_db_subnet_group" "main" {\n'
            f'  name       = "${{var.app_name}}-db-subnet"\n'
            "  subnet_ids = aws_subnet.private[*].id\n"
            "}\n\n"
            'resource "aws_security_group" "rds" {\n'
            f'  name   = "${{var.app_name}}-rds-sg"\n'
            "  vpc_id = aws_vpc.main.id\n\n"
            "  ingress {\n"
            "    from_port       = 5432\n"
            "    to_port         = 5432\n"
            '    protocol        = "tcp"\n'
            "    security_groups = [aws_security_group.ecs.id]\n"
            "  }\n"
            "}\n"
        )

    @staticmethod
    def _generate_networking(name: str) -> str:
        return (
            f"# Networking for {name}\n\n"
            'resource "aws_vpc" "main" {\n'
            '  cidr_block           = "10.0.0.0/16"\n'
            "  enable_dns_hostnames = true\n"
            "  enable_dns_support   = true\n"
            "}\n\n"
            'resource "aws_subnet" "public" {\n'
            "  count             = 2\n"
            "  vpc_id            = aws_vpc.main.id\n"
            '  cidr_block        = "10.0.${count.index + 1}.0/24"\n'
            "  availability_zone = data.aws_availability_zones.available.names[count.index]\n"
            "  map_public_ip_on_launch = true\n"
            "}\n\n"
            'resource "aws_subnet" "private" {\n'
            "  count             = 2\n"
            "  vpc_id            = aws_vpc.main.id\n"
            '  cidr_block        = "10.0.${count.index + 10}.0/24"\n'
            "  availability_zone = data.aws_availability_zones.available.names[count.index]\n"
            "}\n\n"
            'data "aws_availability_zones" "available" {\n'
            '  state = "available"\n'
            "}\n\n"
            'resource "aws_internet_gateway" "main" {\n'
            "  vpc_id = aws_vpc.main.id\n"
            "}\n\n"
            'resource "aws_lb" "main" {\n'
            f'  name               = "${{var.app_name}}-alb"\n'
            "  internal           = false\n"
            '  load_balancer_type = "application"\n'
            "  security_groups    = [aws_security_group.alb.id]\n"
            "  subnets            = aws_subnet.public[*].id\n"
            "}\n\n"
            'resource "aws_lb_target_group" "app" {\n'
            f'  name        = "${{var.app_name}}-tg"\n'
            "  port        = var.container_port\n"
            '  protocol    = "HTTP"\n'
            '  target_type = "ip"\n'
            "  vpc_id      = aws_vpc.main.id\n\n"
            "  health_check {\n"
            '    path = "/api/health"\n'
            "  }\n"
            "}\n\n"
            'resource "aws_security_group" "alb" {\n'
            f'  name   = "${{var.app_name}}-alb-sg"\n'
            "  vpc_id = aws_vpc.main.id\n\n"
            "  ingress {\n"
            '    from_port   = 80\n    to_port     = 80\n    protocol    = "tcp"\n'
            '    cidr_blocks = ["0.0.0.0/0"]\n'
            "  }\n"
            "  ingress {\n"
            '    from_port   = 443\n    to_port     = 443\n    protocol    = "tcp"\n'
            '    cidr_blocks = ["0.0.0.0/0"]\n'
            "  }\n"
            "  egress {\n"
            '    from_port   = 0\n    to_port     = 0\n    protocol    = "-1"\n'
            '    cidr_blocks = ["0.0.0.0/0"]\n'
            "  }\n"
            "}\n\n"
            'resource "aws_security_group" "ecs" {\n'
            f'  name   = "${{var.app_name}}-ecs-sg"\n'
            "  vpc_id = aws_vpc.main.id\n\n"
            "  ingress {\n"
            "    from_port       = var.container_port\n"
            "    to_port         = var.container_port\n"
            '    protocol        = "tcp"\n'
            "    security_groups = [aws_security_group.alb.id]\n"
            "  }\n"
            "  egress {\n"
            '    from_port   = 0\n    to_port     = 0\n    protocol    = "-1"\n'
            '    cidr_blocks = ["0.0.0.0/0"]\n'
            "  }\n"
            "}\n"
        )

    @staticmethod
    def _generate_tfvars(name: str) -> str:
        return (
            f"# {name} Terraform variables\n"
            f'app_name     = "{name}"\n'
            'aws_region   = "us-east-1"\n'
            'environment  = "production"\n'
        )

    @staticmethod
    def get_supported_providers() -> list[str]:
        return ["aws"]
