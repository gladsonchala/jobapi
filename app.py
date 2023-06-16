from fastapi import FastAPI, Response, status
from fastapi import Form
from pydantic import BaseModel
from bson.objectid import ObjectId
import httpx
import os
import uvicorn

app = FastAPI()

# MongoDB Data API configuration
base_url = "https://us-east-2.aws.data.mongodb-api.com/app/data-vagob/endpoint/data/v1"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer gfvvbj"
}

# Job Model
class Job(BaseModel):
    title: str
    description: str
    category: str
    location: str
    price: float
    duration: str
    status: str
    is_emergency: bool
    task_giver_id: str
    photos: str

# Application Model
class Application(BaseModel):
    job_id: str
    user_id: str

# Create a job
@app.post("/jobs")
async def create_job(job: Job):
    try:
        # Make a request to MongoDB Data API to create the job
        url = f"{base_url}/insertOne"
        payload = {
            "database": "agelgilotify",
            "collection": "jobs",
            "document": job.dict()
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code == status.HTTP_200_OK:
            job_id = response.json()["insertedId"]
            return {"message": "Job created", "id": job_id}
        elif response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            return {"message": "Failed to create a job: Internal server error"}
        else:
            return {"message": f"Failed to create a job: {response.json()['message']}"}

    except Exception as ex:
        error_message = "Error creating a job: " + str(ex)
        print(error_message)
        return {"message": error_message}

# Get all jobs
@app.get("/jobs")
async def get_jobs():
    try:
        # Make a request to MongoDB Data API to get all jobs
        url = f"{base_url}/find"
        payload = {
            "database": "agelgilotify",
            "collection": "jobs",
            "limit": 100
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code == status.HTTP_200_OK:
            jobs = response.json()["documents"]
            for job in jobs:
                job["_id"] = str(job["_id"])
            return jobs
        else:
            return {"message": "Failed to fetch jobs"}

    except Exception as ex:
        error_message = "Error fetching jobs: " + str(ex)
        print(error_message)
        return {"message": error_message}

# Get a job by ID
@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    try:
        # Make a request to MongoDB Data API to get the job by ID
        url = f"{base_url}/findOne"
        payload = {
            "database": "agelgilotify",
            "collection": "jobs",
            "filter": {"_id": ObjectId(job_id)}
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code == status.HTTP_200_OK:
            job = response.json()["document"]
            if job:
                job["_id"] = str(job["_id"])
                return job
            else:
                return {"message": "Job not found"}
        else:
            return {"message": "Failed to fetch the job"}

    except Exception as ex:
        error_message = "Error fetching a job: " + str(ex)
        print(error_message)
        return {"message": error_message}

# Update a job
@app.put("/jobs/{job_id}")
async def update_job(job_id: str, job: Job):
    try:
        updated_job = job.dict()

        # Make a request to MongoDB Data API to update the job
        url = f"{base_url}/updateOne"
        payload = {
            "database": "agelgilotify",
            "collection": "jobs",
            "filter": {"_id": ObjectId(job_id)},
            "update": {"$set": updated_job}
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code == status.HTTP_200_OK:
            if response.json()["matchedCount"] > 0:
                return {"message": "Job updated"}
            else:
                return {"message": "Job not found"}
        else:
            return {"message": "Failed to update the job"}

    except Exception as ex:
        error_message = "Error updating a job: " + str(ex)
        print(error_message)
        return {"message": error_message}

# Delete a job
@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    try:
        # Make a request to MongoDB Data API to delete the job
        url = f"{base_url}/deleteOne"
        payload = {
            "database": "agelgilotify",
            "collection": "jobs",
            "filter": {"_id": ObjectId(job_id)}
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code == status.HTTP_200_OK:
            if response.json()["deletedCount"] > 0:
                return {"message": "Job deleted"}
            else:
                return {"message": "Job not found"}
        else:
            return {"message": "Failed to delete the job"}

    except Exception as ex:
        error_message = "Error deleting a job: " + str(ex)
        print(error_message)
        return {"message": error_message}

# Apply for a job
@app.post("/jobs/apply")
async def apply_for_job(job_id: str = Form(...), user_id: str = Form(...)):
    try:
        application = {
            "job_id": ObjectId(job_id),
            "user_id": ObjectId(user_id),
            "status": "Pending",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "rating": None
        }

        # Make a request to MongoDB Data API to insert the application
        url = f"{base_url}/insertOne"
        payload = {
            "database": "agelgilotify",
            "collection": "applications",
            "document": application
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code == status.HTTP_200_OK:
            if response.json()["insertedId"]:
                return {"message": "Application submitted", "id": str(response.json()["insertedId"])}
            else:
                return {"message": "Failed to submit the application"}
        else:
            return {"message": "Failed to submit the application"}

    except Exception as ex:
        error_message = "Error applying for a job: " + str(ex)
        print(error_message)
        return {"message": error_message}

# Get applications for a job
@app.get("/jobs/{job_id}/applications")
async def get_job_applications(job_id: str):
    try:
        # Make a request to MongoDB Data API to get the applications for the job
        url = f"{base_url}/find"
        payload = {
            "database": "agelgilotify",
            "collection": "applications",
            "filter": {"job_id": ObjectId(job_id)}
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code == status.HTTP_200_OK:
            applications = response.json()["documents"]
            for application in applications:
                application["_id"] = str(application["_id"])
            return applications
        else:
            return {"message": "Failed to fetch the applications"}

    except Exception as ex:
        error_message = "Error fetching the applications: " + str(ex)
        print(error_message)
        return {"message": error_message}

if __name__ == "__main__":
    # Get the port number assigned by Heroku or use a default port
    port = int(os.environ.get("PORT", 8000))
    # Start the server using uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
#fastapi uvicorn httpx
