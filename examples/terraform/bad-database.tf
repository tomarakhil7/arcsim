resource "aws_db_instance" "main" {
  identifier     = "api-db"
  engine         = "postgres"
  engine_version = "15.3"
  instance_class = "db.t3.medium"

  allocated_storage = 100
  storage_type      = "gp3"

  db_name  = "main"
  username = "admin"
  password = "changeme"  # Don't do this in real life!

  multi_az = false  # 🔴 DB SPOF in production!

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  skip_final_snapshot = true

  tags = {
    Name        = "api-database"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}
