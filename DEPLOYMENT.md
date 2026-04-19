# CLFMS Deployment Guide

## Production Deployment Checklist

### Pre-Deployment

- [ ] Review code changes and test coverage
- [ ] Update version number in package metadata
- [ ] Run full test suite and ensure 100% pass
- [ ] Verify all environment variables are configured
- [ ] Backup existing database
- [ ] Create deployment backup/snapshot

### Security Configuration

- [ ] Change `SECRET_KEY` to strong random value (min 32 chars)
- [ ] Set `DEBUG=False` in production
- [ ] Configure HTTPS/SSL certificates
- [ ] Setup CORS properly for your domain
- [ ] Enable rate limiting
- [ ] Configure password policies
- [ ] Setup MFA for admin accounts
- [ ] Review database permissions

### Database Configuration

- [ ] Switch from SQLite to PostgreSQL (or preferred DB)
- [ ] Setup database connection pooling
- [ ] Configure backup strategy (daily snapshots)
- [ ] Setup read replicas for high availability
- [ ] Test disaster recovery procedures
- [ ] Configure monitoring and alerting

### Infrastructure

- [ ] Setup containerization (Docker)
- [ ] Configure container orchestration (K8s/Docker Swarm)
- [ ] Setup load balancer
- [ ] Configure reverse proxy (nginx/Apache)
- [ ] Setup CDN for static assets
- [ ] Configure monitoring and logging (ELK/Prometheus)
- [ ] Setup performance monitoring (APM)

### Application Setup

- [ ] Install all production dependencies
- [ ] Run database migrations
- [ ] Create initial admin user
- [ ] Setup email service
- [ ] Configure logging aggregation
- [ ] Setup background job processing (Celery)
- [ ] Configure caching layer (Redis)

## Docker Deployment

### Build Image

```bash
docker build -t clfms:1.0.0 .
docker tag clfms:1.0.0 your-registry/clfms:1.0.0
docker push your-registry/clfms:1.0.0
```

### Docker Compose (Production)

```yaml
version: "3.8"

services:
  web:
    image: your-registry/clfms:1.0.0
    container_name: clfms-api
    restart: always
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/clfms
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=False
    depends_on:
      - postgres
      - redis
    volumes:
      - ./uploads:/app/uploads
    networks:
      - clfms-network

  postgres:
    image: postgres:15-alpine
    container_name: clfms-db
    restart: always
    environment:
      - POSTGRES_USER=clfms
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=clfms
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - clfms-network

  redis:
    image: redis:7-alpine
    container_name: clfms-cache
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - clfms-network

  nginx:
    image: nginx:alpine
    container_name: clfms-proxy
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - web
    networks:
      - clfms-network

volumes:
  postgres-data:
  redis-data:

networks:
  clfms-network:
    driver: bridge
```

### Run with Docker Compose

```bash
docker-compose -f docker-compose.yml up -d
```

## Kubernetes Deployment

### Create Namespace

```bash
kubectl create namespace clfms
```

### Create Secrets

```bash
kubectl create secret generic clfms-secrets \
  --from-literal=SECRET_KEY=$(openssl rand -base64 32) \
  --from-literal=DB_PASSWORD=$(openssl rand -base64 32) \
  -n clfms
```

### Deploy Application

```bash
kubectl apply -f k8s/deployment.yml -n clfms
kubectl apply -f k8s/service.yml -n clfms
kubectl apply -f k8s/ingress.yml -n clfms
```

### Check Deployment Status

```bash
kubectl get pods -n clfms
kubectl logs -f deployment/clfms-api -n clfms
```

## Monitoring & Logging

### Application Logging

```python
# Configure in app/core/config.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/clfms.log'),
        logging.StreamHandler()
    ]
)
```

### Health Checks

```bash
# Endpoint health check
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/health/db

# Cache health
curl http://localhost:8000/health/cache
```

### Metrics Collection

```bash
# Prometheus metrics endpoint
curl http://localhost:8000/metrics
```

## Performance Optimization

### Database

- Enable query caching
- Create indexes on frequently queried fields
- Use connection pooling (pgBouncer)
- Regular VACUUM and ANALYZE

### Application

- Enable response caching headers
- Compress responses (gzip)
- Use async operations for I/O
- Implement lazy loading

### Infrastructure

- Use CDN for static assets
- Setup HTTP/2 support
- Enable HSTS headers
- Configure proper timeouts

## Backup Strategy

### Daily Backups

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups/clfms"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump -h postgres -U clfms clfms > "$BACKUP_DIR/db_$TIMESTAMP.sql"

# File uploads backup
tar -czf "$BACKUP_DIR/uploads_$TIMESTAMP.tar.gz" /app/uploads

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -mtime +30 -delete
```

### Weekly Full Backups

```bash
#!/bin/bash
# full-backup.sh
aws s3 sync /backups/clfms s3://clfms-backups/$(date +%Y%m%d)/
```

## Monitoring & Alerting

### Key Metrics to Monitor

- API response times (target: <500ms)
- Error rate (target: <0.1%)
- Database query performance
- Disk usage
- Memory usage
- CPU usage
- Request rate (requests/second)

### Alerting Rules

```yaml
# prometheus-rules.yml
groups:
  - name: clfms
    rules:
      - alert: HighErrorRate
        expr: rate(http_errors_total[5m]) > 0.001
        for: 5m
        action: notify_ops

      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 1
        for: 5m
        action: notify_ops

      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        action: notify_ops_critical
```

## Rollback Procedures

### Database Rollback

```bash
# List available backups
ls -la /backups/clfms/

# Restore from backup
psql -h postgres -U clfms clfms < /backups/clfms/db_20260419_120000.sql

# Verify restoration
psql -h postgres -U clfms clfms -c "SELECT COUNT(*) FROM users;"
```

### Application Rollback

```bash
# Revert to previous image
docker pull your-registry/clfms:1.0.0
docker-compose up -d

# Or with Kubernetes
kubectl rollout undo deployment/clfms-api -n clfms
```

## Post-Deployment Validation

- [ ] API responds to requests
- [ ] Authentication works
- [ ] All endpoints functional
- [ ] Dashboard displays correctly
- [ ] Financial calculations accurate
- [ ] Reports generate properly
- [ ] Email notifications working
- [ ] Logging captures events
- [ ] Performance within SLA

## Incident Response

### High Error Rate

1. Check application logs
2. Verify database connectivity
3. Check recent deployments
4. Monitor CPU/memory usage
5. Consider rollback if necessary

### Database Performance

1. Check active queries
2. Analyze slow query logs
3. Consider index optimization
4. Check connection pool usage
5. Scale database if needed

### Security Incident

1. Check access logs
2. Identify compromised credentials
3. Rotate secrets
4. Reset affected user sessions
5. Review recent changes

## Support Contacts

- **Development Team**: dev@clfms.local
- **Operations Team**: ops@clfms.local
- **Security Team**: security@clfms.local
- **On-Call**: See runbook in wiki

---

Last Updated: April 19, 2026
Version: 1.0.0
