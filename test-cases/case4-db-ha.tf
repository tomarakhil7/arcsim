resource "aws_db_instance" "orders" {
  identifier     = "orders-database"
  engine         = "postgres"
  engine_version = "15.3"
  instance_class = "db.t3.large"

  allocated_storage = 100
  storage_type      = "gp3"

  multi_az = false  # No HA in production!

  username = "orderadmin"
  password = var.db_password

  backup_retention_period = 7
  backup_window          = "03:00-04:00"

  tags = {
    Name        = "orders-database"
    Environment = "production"
  }
}
