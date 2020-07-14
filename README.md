# indeed_parser_API

### This repository is organized in 2 folders :

## indeed_scrapper

**indeed_scrapper** let you retrieve job offers on **indeed.fr**

The script uses the **Selenium API** to automatize the scrapping of job offers

* **indeed_scrapper.py** : Contains the python script to scrap data on the indeed.fr website

* **job_offers.csv** : CSV file containing approx. 200 lines of scrapped job offers

| Column | Description |
| --- | --- |
| **job_name** | Name of the job |
| **company** | Company emitting the job offer |
| **location** | Location of the job offer |
| **department** | Department where the job offer is located |
| **easy_apply** | Whether you can apply using embed Indeed tool |
| **salary** | Salary for the job offer |
| **remote** | Whether the job is remote |
| **urgently_hiring** | Whether the company is hiring urgently |
| **company_rating** | Rating of the company emitting the job offer |

How to use :

1. Type `python indeed_scrapper.py`

2. Chrome tab will appear

3. Wait until the chrome tab disapear

4. Data are saved under `indeed_scrapper\job_offers.csv`

## indeed_API

**indeed_API** will expose the data retrieved previously using Flask-RESTPlus, an extension for Flask

* **api.py** : Contains the python code to run the Flask API

* **indeed_API.postman_collection.json** : JSON file containing a **Postman** requests collection to test the API with samples

How to use :

1. Type `python indeed_API.py`

2. navigate to `http://127.0.0.1:5000/`
