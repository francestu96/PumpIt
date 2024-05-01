FROM node:18-alpine

WORKDIR /pump_it

COPY ./pump_it.mjs ./package.json ./.env .
COPY ./ABIs ./ABIs

RUN npm install

CMD [ "node", "--no-warnings", "pump_it.mjs", "0.005" ]