import inspect
import os
from urllib.parse import urlparse, urlunparse
from typing import Any, Optional, Type
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ConfigDict

load_dotenv()

try:
    from qdrant_client import QdrantClient

    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    QdrantClient = Any  # type placeholder

from crewai.tools import BaseTool


class QdrantSearchToolSchema(BaseModel):
    """Input for QdrantSearchTool."""

    query: str = Field(
        ...,
        description="The word or phrase to search for in the astrology reference docs. Use SHORT, technical astrological terms ONLY to match on similarity.",
    )


class QdrantSearchTool(BaseTool):
    """
    Custom tool to search a Qdrant database for relevant information,
    specifically designed for the astrology reference docs collection.
    """
    client: QdrantClient = None
    name: str = "QdrantSearchTool"
    description: str = (
        "A tool to search astrology reference docs for relevant information"
    )
    args_schema: Type[BaseModel] = QdrantSearchToolSchema
    collection_name: str = Field(
        default=os.environ.get("QDRANT_COLLECTION_NAME"), description="Name of the Qdrant collection to search."
    )
    limit: int = Field(default=5, description="Maximum number of results to return.")
    score_threshold: float = Field(
        default=0.2, description="Minimum similarity score threshold."
    )
    qdrant_url: Optional[str] = Field(
        default=None, description="The URL of the Qdrant server."
    )
    qdrant_api_key: Optional[str] = Field(
        default=None, description="The API key for the Qdrant server."
    )
    custom_embedding_fn: Optional[callable] = Field(
        default=None,
        description="Optional custom embedding function. Defaults to Gemini embeddings.",
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)


    @staticmethod
    def _normalize_qdrant_url(raw_url: str) -> str:
        url = (raw_url or "").strip().rstrip("/")
        if not url:
            return url
        if "://" not in url:
            url = f"https://{url}"
        parsed = urlparse(url)
        netloc = parsed.netloc
        path = parsed.path
        if not netloc and path:
            netloc = path
            path = ""
        if ":" not in netloc:
            netloc = f"{netloc}:6333"
        return urlunparse((parsed.scheme, netloc, path, "", "", ""))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.qdrant_url = os.environ.get("QDRANT_LOCAL_URL")
        self.qdrant_api_key = os.environ.get("QDRANT_LOCAL_API_KEY")
        if self.qdrant_url:
            self.qdrant_url = self._normalize_qdrant_url(self.qdrant_url)
        self.collection_name = os.environ.get(
            "QDRANT_COLLECTION_NAME", "astro_knowledge"
        )  # Use env, fallback to default

        if not self.qdrant_url or not self.qdrant_api_key:
            raise ValueError(
                "QDRANT_LOCAL_URL and QDRANT_LOCAL_API_KEY must be set as environment variables."
            )

        if QDRANT_AVAILABLE:
            self.client = self._build_client(self.qdrant_url)
        else:
            raise ImportError(
                "The 'qdrant-client' package is required.  Install it with: pip install qdrant-client"
            )

    def _build_client(self, url: str) -> QdrantClient:
        client_kwargs = {
            "url": url,
            "api_key": self.qdrant_api_key,
        }
        if "check_compatibility" in inspect.signature(QdrantClient).parameters:
            client_kwargs["check_compatibility"] = False
        return QdrantClient(**client_kwargs)

    def _fallback_to_https_443(self) -> Optional[str]:
        if not self.qdrant_url:
            return None
        parsed = urlparse(self.qdrant_url)
        if parsed.port != 6333 or not parsed.hostname:
            return None
        alt_netloc = f"{parsed.hostname}:443"
        alt_url = urlunparse((parsed.scheme, alt_netloc, parsed.path, "", "", ""))
        self.qdrant_url = alt_url
        self.client = self._build_client(alt_url)
        return alt_url

    def _run(
        self,
        query: str,
    ) -> str:
        """Execute vector similarity search on Qdrant."""

        if not self.client:
            return "Qdrant client not initialized."

        if hasattr(self.client, "collection_exists"):
            try:
                if not self.client.collection_exists(self.collection_name):
                    return (
                        f"Qdrant collection '{self.collection_name}' not found. Set QDRANT_COLLECTION_NAME or run the Qdrant setup."
                    )
            except Exception as e:
                if "404" in str(e):
                    fallback_url = self._fallback_to_https_443()
                    if fallback_url:
                        try:
                            if not self.client.collection_exists(self.collection_name):
                                return (
                                    f"Qdrant collection '{self.collection_name}' not found. Set QDRANT_COLLECTION_NAME or run the Qdrant setup."
                                )
                        except Exception as fallback_error:
                            return (
                                "Error checking Qdrant collection after HTTPS:443 fallback: "
                                f"{fallback_error}"
                            )
                return f"Error checking Qdrant collection: {e}"

        search_filter = None

        try:
            if self.custom_embedding_fn:
                query_vector = self.custom_embedding_fn(query)
            else:
                # Use the custom Gemini embedding function from utils
                from transit_reader.utils.embeddings_fn import (
                    custom_gemini_embedding_fn,
                )

                query_vector = custom_gemini_embedding_fn(query)

            if query_vector is None:
                return "Error: Could not generate embedding for the query."

            search_results = self._search_qdrant(query_vector, search_filter)
            points = self._extract_points(search_results)

            results = []
            for point in points:
                payload = getattr(point, "payload", {}) or {}
                results.append(
                    {
                        "metadata": payload.get("source", ""),
                        "context": payload.get("text", ""),
                        "score": getattr(point, "score", None),
                    }
                )
            return str(results)

        except Exception as e:
            return f"Error during Qdrant search: {e}"

    def _search_qdrant(self, query_vector, search_filter):
        """Run a Qdrant search compatible with both legacy and new client APIs."""
        base_kwargs = dict(
            collection_name=self.collection_name,
            limit=self.limit,
            score_threshold=self.score_threshold,
            with_payload=True,
            with_vectors=False,
        )
        filter_kwargs = dict(query_filter=search_filter, filter=search_filter)

        if hasattr(self.client, "search"):
            method = self.client.search
            vector_kwargs = self._select_vector_kwargs(
                method, query_vector, preferred=("query_vector", "vector")
            )
            if vector_kwargs:
                return self._call_with_supported_params(
                    method, **base_kwargs, **filter_kwargs, **vector_kwargs
                )

        if hasattr(self.client, "query_points"):
            method = self.client.query_points
            vector_kwargs = self._select_vector_kwargs(
                method, query_vector, preferred=("query", "query_vector", "vector")
            )
            if vector_kwargs:
                return self._call_with_supported_params(
                    method, **base_kwargs, **filter_kwargs, **vector_kwargs
                )

        if hasattr(self.client, "query"):
            method = self.client.query
            sig = inspect.signature(method)
            if "query_text" in sig.parameters and not any(
                name in sig.parameters
                for name in ("query_vector", "query", "vector")
            ):
                raise AttributeError(
                    "Connected QdrantClient.query expects a text query; vector search is unavailable."
                )
            vector_kwargs = self._select_vector_kwargs(
                method, query_vector, preferred=("query_vector", "query", "vector")
            )
            if vector_kwargs:
                return self._call_with_supported_params(
                    method, **base_kwargs, **filter_kwargs, **vector_kwargs
                )

        raise AttributeError(
            "Connected QdrantClient does not provide a vector search method."
        )

    @staticmethod
    def _call_with_supported_params(method, **kwargs):
        """Call a method using only parameters it explicitly supports."""
        sig = inspect.signature(method)
        supported = {
            name: value
            for name, value in kwargs.items()
            if name in sig.parameters and value is not None
        }
        return method(**supported)

    @staticmethod
    def _select_vector_kwargs(method, query_vector, preferred):
        """Pick the first supported vector argument name for this method."""
        sig = inspect.signature(method)
        for name in preferred:
            if name in sig.parameters:
                return {name: query_vector}
        return {}

    @staticmethod
    def _extract_points(search_results):
        """Normalize different Qdrant responses to an iterable of points."""
        if hasattr(search_results, "points"):
            return search_results.points
        return search_results or []


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    # Example usage with dummy environment variables
    os.environ["QDRANT_LOCAL_URL"] = "http://localhost:6333"  # your qdrant url
    os.environ["QDRANT_LOCAL_API_KEY"] = os.environ.get("QDRANT_LOCAL_API_KEY")  # your qdrant api key
    os.environ["GEMINI_API_KEY"] = os.environ.get("GEMINI_API_KEY") # your gemini api key

    if (
        not os.environ.get("QDRANT_LOCAL_URL")
        or not os.environ.get("QDRANT_LOCAL_API_KEY")
        or not os.environ.get("GEMINI_API_KEY")
    ):
        print(
            "Please set QDRANT_LOCAL_URL, QDRANT_LOCAL_API_KEY and GEMINI_API_KEY environment variables."
        )
        exit(1)

    tool = QdrantSearchTool()
    query = "What is the ruler of the 1st house?"
    result = tool._run(query=query)
    print(result) 
