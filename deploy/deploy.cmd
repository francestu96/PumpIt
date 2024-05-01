tar -czf deploy/pumpit.tar.gz ./ABIs ./node_modules ./.env ./pump_it.mjs
scp -i deploy/LightsailDefaultKey-eu-central-1.pem deploy/pumpit.tar.gz ubuntu@18.192.214.35:/home/ubuntu/pump_it
del deploy\pumpit.tar.gz
ssh -i deploy/LightsailDefaultKey-eu-central-1.pem ubuntu@18.192.214.35 "tar -xzf ./pump_it/pumpit.tar.gz -C ./pump_it; rm ./pump_it/pumpit.tar.gz; sudo systemctl restart pump_it.service"