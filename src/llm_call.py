import os
import requests

from google.oauth2 import service_account
from google.auth.transport.requests import Request
from langchain_core.callbacks import CallbackManagerForLLMRun
from typing import Any, Optional, ClassVar
from langchain_core.language_models.llms import LLM


# Set proxy environment variables for DB network
os.environ['HTTP_PROXY'] = 'http://sp-surf-proxy.intranet.db.com:8080'
os.environ['HTTPS_PROXY'] = 'http://sp-surf-proxy.intranet.db.com:8080'


class VertexAILangchainLLM(LLM):
    """
    LangChain LLM class for interacting with Vertex AI using direct HTTP requests.
    """
    project_id: ClassVar[str] = "db-dev-ny3a-flare-dev-1"
    location:ClassVar[str] = "europe-west3"
    model_name:ClassVar[str] = "gemini-1.5-pro-002"
    credentials_path:ClassVar[str] = 'keyfile_new.json'
    if os.getenv('HTTP_PROXY'):
        proxies = {
            'http': os.getenv('HTTP_PROXY'),
            'https': os.getenv('HTTPS_PROXY')
        }   
    else:
        proxies = {}

    temperature: int = 0
    credentials: str = ""

    def __init__(self, model_params: dict):
        """
        Initialize the VertexAILangchainLLM.

        Args:
            model_params: A dictionary containing model parameters.
                - location: The location of the Vertex AI endpoint.
                - model_name: The name of the model to use.
                - temperature: The temperature for text generation.
                - credentials_path: Optional path to service account key file.
        """
        super().__init__()
        if 'temperature' not in model_params:
            model_params['temperature'] = 0.5
        else:
            self.temperature = model_params['temperature']

        # if 'location' not in model_params:
        #     raise ValueError("location must be provided in model_params")

        # if 'model_name' not in model_params:
        #     raise ValueError("model_name must be provided in model_params")
        

        self.authenticate()

    @property
    def _llm_type(self) -> str:
        return "custom"

    def authenticate(self):
        """
        Authenticate with Vertex AI using service account credentials.

        Args:
            project_id: The GCP project ID
            credentials_path: Optional path to service account key file
        """

        if self.credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path

        if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not set")

        self.credentials = service_account.Credentials.from_service_account_file(
            os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )

    def _call(self,
              prompt: str,
              run_manager: Optional[CallbackManagerForLLMRun] = None,
              **kwargs: Any
              ) -> str:
        try:
            if not self.credentials.valid:
                self.credentials.refresh(Request())

            url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.model_name}:generateContent"

            headers = {
                "Authorization": f"Bearer {self.credentials.token}",
                "Content-Type": "application/json",
                "x-goog-request-params": "vpc-sc-bypass=true",
                "x-goog-user-project": self.project_id,
                "x-goog-vpc-service-controls": "true"
            }

            data = {
                "contents": [{
                    "role": "user",
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": self.temperature
                }
            }

            response = requests.post(url, headers=headers, json=data) #proxies=self.proxies)
            if response.status_code == 200:
                response_json = response.json()
                if 'candidates' in response_json and len(response_json['candidates']) > 0:
                    text = response_json['candidates'][0]['content']['parts'][0]['text']
                    return text
                raise Exception("No text found in response")
            else:
                error_message = response.text
                print(f"Full error: {error_message}")
                if "VPC_SERVICE_CONTROLS" in error_message:
                    raise Exception("Please ensure you're connected to DB VPN")
                elif "PERMISSION_DENIED" in error_message:
                    raise Exception("Check service account permissions")
                else:
                    raise Exception(f"API Error: {error_message}")

        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {str(e)}")
            raise
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            raise