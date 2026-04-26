import os
import httpx
from typing import Dict, Any, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class CivicApiService:
    """
    Service to interact with the Google Civic Information API.
    Provides data on elections, polling places, and voter information.
    """
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_CIVIC_API_KEY")
        self.base_url = "https://www.googleapis.com/civicinfo/v2"
        
        if not self.api_key:
            # Note: In a production app, we would log a warning here if not provided
            pass

    async def get_voter_info(self, address: str, election_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Retrieves voter-specific information (polling places, ballots) using an address.
        
        Args:
            address: The user's address to look up information for.
            election_id: Optional specific election ID to query.
            
        Returns:
            Dictionary containing the API response data.
        """
        endpoint = f"{self.base_url}/voterinfo"
        params = {
            "key": self.api_key,
            "address": address
        }
        if election_id:
            params["electionId"] = election_id
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                return {"error": f"API Error: {e.response.status_code}", "details": e.response.text}
            except Exception as e:
                return {"error": "Internal Error", "details": str(e)}

    async def get_elections(self) -> Dict[str, Any]:
        """
        Retrieves a list of upcoming elections.
        """
        endpoint = f"{self.base_url}/elections"
        params = {"key": self.api_key}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"error": "Failed to fetch elections", "details": str(e)}

# Singleton instance
civic_service = CivicApiService()
