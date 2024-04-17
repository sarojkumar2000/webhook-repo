# webhook-repo

### This Flask application receives GitHub webhook events and stores them in a MongoDB database.

 #### Installation 
- Install Docker in your machine.
- Install Ngrok ( https://ngrok.com/download) and create account in Ngrok use token for configuration

1. Clone this repository to yourmachine:

  git clone https://github.com/sarojkumar2000/webhook-repo.git

2. Navigate to project directory:
   
  cd repository name
  
3. Build and start the Docker container:
   
  docker-compose up --build
  
4. command to start the application container:

  docker-compose up -d github_events
  
5.  Expose flask app to Ngrok
   
  ./ngrok http 5000
  
6. To stop docker container
   
  docker-compose stop


#### API Endpoints
- "/events": GET request to retrieve all stored GitHub events.
- "/webhook": POST request to handle GitHub webhook events.


