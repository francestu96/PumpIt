aws ecr-public batch-delete-image --repository-name pumpit --image-ids imageTag=latest --region us-east-1
docker build -t public.ecr.aws/h6c9y0s0/pumpit:latest -f ./deploy/Dockerfile .
docker push public.ecr.aws/h6c9y0s0/pumpit:latest
docker image rm public.ecr.aws/h6c9y0s0/pumpit:latest
aws ecs update-service --cluster PumpIt --service PumpIt-svc --force-new-deployment --region eu-central-1 --no-cli-pager