aws ecr-public batch-delete-image --repository-name soltrendsniperbot --image-ids imageTag=latest --region us-east-1
docker build -t public.ecr.aws/h6c9y0s0/soltrendsniperbot:latest -f ./deploy/Dockerfile .
docker push public.ecr.aws/h6c9y0s0/soltrendsniperbot:latest
aws ecs update-service --cluster SolTrendSniperBot --service SolTrendSniperBot-svc --force-new-deployment --region eu-central-1