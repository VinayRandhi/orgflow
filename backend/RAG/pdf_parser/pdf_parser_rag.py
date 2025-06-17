import logging
import os
from io import BytesIO
from typing import List, Tuple, Optional, Dict, Any
import pdfplumber
from PIL import Image
import numpy as np
from openai import OpenAI, AzureOpenAI
import base64
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import asyncio
from tqdm import tqdm
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('pdf_parser.log')
    ]
)

@dataclass
class Chunk:
    text: str
    metadata: Dict[str, Any]
    page_number: int
    position: Optional[Tuple[float, float, float, float]] = None  # x0, y0, x1, y1

class PDFParserRAG:
    def __init__(self, openai_api_key: str, model: str = "gpt-4o"):
        """
        Initialize the PDF parser for RAG applications.
        
        Args:
            openai_api_key: OpenAI API key for GPT-4 Vision model
            model: OpenAI model to use for vision processing
        """
        logging.info(f"Initializing PDFParserRAG with model: {model}")
        self.client = AzureOpenAI(api_key=openai_api_key, api_version="2024-12-01-preview")
        self.model = model
        self.vision_prompt = """Analyze this PDF page image and extract the following information:
1. Main text content with proper formatting and structure
2. Headers and their hierarchy
3. Tables (if any) in a structured format
4. Lists and bullet points
5. Important figures or diagrams (describe them)

Please maintain the original document structure and formatting. For tables, preserve the column structure.
For headers, indicate their level (H1, H2, etc.).
For lists, maintain the bullet points or numbering.

Format the output as follows:
[HEADER] Level: [level] Text: [header text]
[CONTENT] [main text content]
[TABLE] [table content in structured format]
[LIST] [list items]
[FIGURE] [figure description]

Ensure to preserve the logical flow and relationships between different elements."""

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess the image to enhance OCR quality.
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image
        """
        logging.debug("Starting image preprocessing")
        start_time = time.time()
        
        # Convert to RGB if not already
        if image.mode != 'RGB':
            logging.debug("Converting image to RGB")
            image = image.convert('RGB')
            
        # Enhance contrast
        from PIL import ImageEnhance
        logging.debug("Enhancing image contrast")
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Increase resolution for better OCR
        width, height = image.size
        logging.debug(f"Resizing image from {width}x{height} to {width*2}x{height*2}")
        image = image.resize((width * 2, height * 2), Image.Resampling.LANCZOS)
        
        processing_time = time.time() - start_time
        logging.debug(f"Image preprocessing completed in {processing_time:.2f} seconds")
        return image

    def _encode_image(self, image: Image.Image) -> str:
        """
        Encode image to base64 for OpenAI API.
        
        Args:
            image: PIL Image object
            
        Returns:
            Base64 encoded string
        """
        logging.debug("Encoding image to base64")
        start_time = time.time()
        
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        encoded = base64.b64encode(buffered.getvalue()).decode()
        
        encoding_time = time.time() - start_time
        logging.debug(f"Image encoding completed in {encoding_time:.2f} seconds")
        return encoded

    async def _process_page(self, image: Image.Image, page_num: int) -> Chunk:
        """
        Process a single page using GPT-4 Vision.
        
        Args:
            image: PIL Image object
            page_num: Page number
            
        Returns:
            Chunk object containing extracted text and metadata
        """
        logging.info(f"Processing page {page_num}")
        start_time = time.time()
        
        # Preprocess image
        processed_image = self._preprocess_image(image)
        
        # Encode image
        base64_image = self._encode_image(processed_image)
        
        try:
            logging.info(f"Sending page {page_num} to GPT-4 Vision model")
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.vision_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4096
            )
            
            extracted_text = response.choices[0].message.content
            processing_time = time.time() - start_time
            logging.info(f"Page {page_num} processed successfully in {processing_time:.2f} seconds")
            
            return Chunk(
                text=extracted_text,
                metadata={
                    "page_number": page_num,
                    "model": self.model,
                    "processing_type": "vision",
                    "processing_time": processing_time
                },
                page_number=page_num
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logging.error(f"Error processing page {page_num} after {processing_time:.2f} seconds: {str(e)}")
            return Chunk(
                text="",
                metadata={"error": str(e), "page_number": page_num, "processing_time": processing_time},
                page_number=page_num
            )

    async def process_pdf(self, pdf_path: str, max_workers: int = 4) -> List[Chunk]:
        """
        Process PDF file and extract text using GPT-4 Vision.
        
        Args:
            pdf_path: Path to PDF file
            max_workers: Maximum number of concurrent workers
            
        Returns:
            List of Chunk objects containing extracted text and metadata
        """
        logging.info(f"Starting PDF processing: {pdf_path}")
        start_time = time.time()
        chunks = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                logging.info(f"PDF opened successfully. Total pages: {total_pages}")
                
                # Process pages concurrently
                logging.info(f"Starting concurrent processing with {max_workers} workers")
                async with asyncio.TaskGroup() as tg:
                    tasks = []
                    for page_num in range(total_pages):
                        logging.debug(f"Converting page {page_num + 1} to image")
                        page = pdf.pages[page_num]
                        image = page.to_image(resolution=300).original
                        task = tg.create_task(self._process_page(image, page_num + 1))
                        tasks.append(task)
                    
                    # Collect results
                    for task in tasks:
                        chunk = await task
                        if chunk.text:  # Only add non-empty chunks
                            chunks.append(chunk)
                
                # Sort chunks by page number
                chunks.sort(key=lambda x: x.page_number)
                
                total_time = time.time() - start_time
                logging.info(f"PDF processing completed in {total_time:.2f} seconds")
                logging.info(f"Successfully processed {len(chunks)} out of {total_pages} pages")
                
                return chunks
                
        except Exception as e:
            total_time = time.time() - start_time
            logging.error(f"Error processing PDF {pdf_path} after {total_time:.2f} seconds: {str(e)}")
            return []

    def save_chunks_to_file(self, chunks: List[Chunk], output_path: str):
        """
        Save extracted chunks to a text file.
        
        Args:
            chunks: List of Chunk objects
            output_path: Path to save the output file
        """
        logging.info(f"Saving {len(chunks)} chunks to {output_path}")
        start_time = time.time()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for chunk in chunks:
                f.write(f"=== Page {chunk.page_number} ===\n")
                f.write(chunk.text)
                f.write("\n\n")
        
        save_time = time.time() - start_time
        logging.info(f"Chunks saved successfully in {save_time:.2f} seconds")

if __name__ == "__main__":
    # Example usage
    import os
    from dotenv import load_dotenv
    
    load_dotenv()

    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    
    parser = PDFParserRAG(openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    async def main():
        logging.info("Starting PDF processing example")
        chunks = await parser.process_pdf("FAQs.pdf")
        parser.save_chunks_to_file(chunks, "output.txt")
        logging.info("PDF processing example completed")
    
    asyncio.run(main()) 