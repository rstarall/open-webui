import os
import logging
import requests
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders.base import BaseLoader

from open_webui.env import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["RAG"])


class MinerULoader(BaseLoader):
    def __init__(
        self,
        file_path,
        url: str,
        backend: str = "pipeline",
        sglang_server_url: str = None,
        **kwargs,
    ) -> None:
        self.url = url
        self.file_path = file_path
        self.backend = backend
        self.sglang_server_url = sglang_server_url

    def load(self) -> List[Document]:
        # Prepare the URL
        url = self.url
        if url.endswith("/"):
            url = url[:-1]
        
        full_url = f"{url}/file_parse"
        
        # Prepare the file
        filename = os.path.basename(self.file_path)
        
        # Prepare form data
        with open(self.file_path, "rb") as f:
            files = {"files": (filename, f, "application/pdf")}
            
            # Prepare other form fields
            data = {
                "output_dir": "./output",
                "lang_list": "ch",
                "backend": self.backend,
                "parse_method": "auto",
                "formula_enable": "true",
                "table_enable": "true",
                "return_md": "true"
            }
            
            # Add server_url for vlm-sglang-client backend
            if self.backend == "vlm-sglang-client" and self.sglang_server_url:
                data["server_url"] = self.sglang_server_url
            
            try:
                response = requests.post(full_url, files=files, data=data)
            except Exception as e:
                log.error(f"Error connecting to MinerU endpoint: {e}")
                raise Exception(f"Error connecting to MinerU endpoint: {e}")
        
        if response.ok:
            try:
                response_data = response.json()
                
                # MinerU returns markdown content
                if isinstance(response_data, dict):
                    content = None
                    
                    # Try to get markdown content from response
                    if "markdown" in response_data:
                        content = response_data["markdown"]
                    elif "content" in response_data:
                        content = response_data["content"]
                    elif "text" in response_data:
                        content = response_data["text"]
                    elif "result" in response_data:
                        if isinstance(response_data["result"], str):
                            content = response_data["result"]
                        elif isinstance(response_data["result"], dict) and "markdown" in response_data["result"]:
                            content = response_data["result"]["markdown"]
                    else:
                        content = str(response_data)
                    
                    if content:
                        return [
                            Document(
                                page_content=content,
                                metadata={
                                    "source": filename,
                                    "parser": "MinerU"
                                }
                            )
                        ]
                elif isinstance(response_data, str):
                    # Direct string response
                    return [
                        Document(
                            page_content=response_data,
                            metadata={"source": filename, "parser": "MinerU"}
                        )
                    ]
                else:
                    raise Exception(f"Unexpected response type from MinerU: {type(response_data)}")
            except ValueError as e:
                # If response is not JSON, treat it as plain text
                log.info("MinerU returned non-JSON response, treating as plain text")
                return [
                    Document(
                        page_content=response.text,
                        metadata={"source": filename, "parser": "MinerU"}
                    )
                ]
        else:
            error_msg = f"Error loading document with MinerU: {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail}"
            except:
                error_msg += f" - {response.text}"
            
            raise Exception(error_msg)