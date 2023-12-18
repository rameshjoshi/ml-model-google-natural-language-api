**Use Case** 
You’re working in the IT department of a major metropolitan hospital and have been assigned the job of helping to manage the high volume of email requests by routing the emails to the proper medical department. You decide to test the viability of a system using the Natural Language API to index and then query a number of example emails.

# ml-model-google-natural-language-api

**Enable the API**
  From the Google Cloud console main navigation (hamburger menu on the top left), select APIs & Services > Library.
  In the search box, search for natural language, and select the Cloud Natural Language API tile from the results.
  Click ENABLE.
  
**Authenticate the Service Account**
set the project : 
  $gcloud config set project <PROJECT_ID>
  $export GOOGLE_APPLICATION_CREDENTIALS="sa-key.json

**Index the Example Files**
  Run the following command to index the sample files:
  
  python classify_text_tutorial.py index emails
  Observe a new file, index.json, was created and contains the text.
  
  Re-open the Cloud Editor to see the new index.json file. Click the file to open it and review the returned JSON.

**Query the Index**
  Go back to the Cloud Shell, and query the new file for the Arthritis category:
  
  python classify_text_tutorial.py query-category index.json "Health/Health Conditions/Arthritis"
  Observe that three indexed texts were found. Observe the similarity ratings, with email01 having the highest similarity.
  
  Perform another query for Diabetes:
  
  python classify_text_tutorial.py query-category index.json "Health/Health Conditions/Diabetes"
  Observe that three indexed texts were also found. Observe that the emails have a higher similarity rating for this category than the previous query.
  
  Go back to the Cloud Editor, and review the categorizations for the emails in the index.json file:
  
  email01 specifies only Arthritis.
  email02 shows two possible categorizations: Endocrine Conditions and Diabetes.
  email03 doesn't specify any particular condition.
  Review the original emails from the directory navigation on the left, under the emails folder. Can you observe any patterns or make additional inferences based on the results?
![image](https://github.com/rameshjoshi/ml-model-google-natural-language-api/assets/7277702/2cb31205-fa36-4738-b06f-0cb72fb20328)


