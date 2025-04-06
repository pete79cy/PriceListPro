import os
from openai import OpenAI
from utils.logger import logger
from models import FileUpload, Quotation, Invoice, Customer, Product, PriceList
from datetime import datetime
from functools import lru_cache

# Singleton pattern for document analyzer
_document_analyzer_instance = None

def get_document_analyzer():
    """Get or create the document analyzer singleton instance"""
    global _document_analyzer_instance
    if _document_analyzer_instance is None:
        _document_analyzer_instance = DocumentAnalyzer()
    return _document_analyzer_instance

def reset_document_analyzer():
    """Reset the document analyzer singleton, forcing it to reload with new settings"""
    global _document_analyzer_instance
    logger.info("Resetting document analyzer singleton")
    _document_analyzer_instance = None
    return get_document_analyzer()

class DocumentAnalyzer:
    """
    AI-powered document analyzer that provides contextual insights
    for uploaded documents, quotations, and invoices.
    """
    
    def __init__(self):
        """Initialize the document analyzer with OpenAI API key from environment"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
            logger.warning("OpenAI API key not found. Document insights disabled.")
        
        # Initialize analysis cache
        self._analysis_cache = {}
    
    def is_enabled(self):
        """Check if the analyzer is enabled (API key is set)"""
        return self.enabled
    
    def analyze_document(self, document_type, document_id, file_content=None):
        """
        Analyze a document and return insights
        
        Args:
            document_type: Type of document ('quotation', 'invoice', 'excel', 'pdf')
            document_id: ID of the document in the database
            file_content: Optional raw file content for direct analysis
            
        Returns:
            dict: A dictionary containing insights and recommendations
        """
        start_time = datetime.now()
        logger.info(f"Starting analysis of {document_type} #{document_id}")
        
        # Validate inputs
        if not document_type:
            logger.error("Document type not provided")
            return {"error": "Document type is required", "error_code": "MISSING_DOCUMENT_TYPE"}
            
        if not document_id:
            logger.error("Document ID not provided")
            return {"error": "Document ID is required", "error_code": "MISSING_DOCUMENT_ID"}
        
        # Check if AI analysis is enabled
        if not self.enabled:
            logger.warning("AI document analysis was requested but is not enabled")
            return {
                "error": "AI document analysis is not enabled. Please add an OpenAI API key.",
                "error_code": "AI_NOT_ENABLED",
                "resolution": "Add your OpenAI API key in the system settings"
            }
        
        # Check cache first - using a cache key based on document type and ID
        cache_key = f"{document_type}_{document_id}"
        if cache_key in self._analysis_cache:
            logger.info(f"Using cached analysis for {document_type} #{document_id}")
            return self._analysis_cache[cache_key]
        
        # Valid document types
        valid_types = ['quotation', 'invoice', 'excel', 'pdf']
        if document_type not in valid_types:
            logger.error(f"Invalid document type: {document_type}")
            return {
                "error": f"Unknown document type: {document_type}. Valid types are: {', '.join(valid_types)}",
                "error_code": "INVALID_DOCUMENT_TYPE"
            }
        
        try:
            # Get relevant document context
            context = self._get_document_context(document_type, document_id, file_content)
            
            # Check if context retrieval had errors
            if context.get("error"):
                logger.error(f"Error retrieving context: {context['error']}")
                return context
            
            # Define specific prompts based on document type
            if document_type == 'quotation':
                insights = self._analyze_quotation(context)
            elif document_type == 'invoice':
                insights = self._analyze_invoice(context)
            elif document_type == 'excel':
                insights = self._analyze_excel(context)
            elif document_type == 'pdf':
                insights = self._analyze_pdf(context)
            
            # Cache the results (don't cache errors)
            if "error" not in insights:
                self._analysis_cache[cache_key] = insights
                logger.info(f"Cached analysis for {document_type} #{document_id}")
            else:
                logger.warning(f"Analysis completed with errors: {insights['error']}")
            
            # Log duration for performance monitoring
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Analysis of {document_type} #{document_id} completed in {duration:.2f} seconds")
            
            return insights
        
        except ValueError as ve:
            # Handle value errors (missing fields, invalid formats)
            error_msg = str(ve)
            logger.error(f"Value error during document analysis: {error_msg}")
            return {
                "error": f"Analysis failed due to invalid data: {error_msg}",
                "error_code": "INVALID_DATA_FORMAT"
            }
        except TypeError as te:
            # Handle type errors (wrong data types)
            error_msg = str(te)
            logger.error(f"Type error during document analysis: {error_msg}")
            return {
                "error": f"Analysis failed due to data type mismatch: {error_msg}",
                "error_code": "DATA_TYPE_ERROR"
            }
        except KeyError as ke:
            # Handle missing keys in data structures
            error_msg = str(ke)
            logger.error(f"Key error during document analysis: {error_msg}")
            return {
                "error": f"Analysis failed due to missing data field: {error_msg}",
                "error_code": "MISSING_DATA_FIELD"
            }
        except Exception as e:
            # General exception handler for unexpected errors
            error_msg = str(e)
            import traceback
            logger.error(f"Error analyzing document: {error_msg}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "error": f"Analysis failed: {error_msg}",
                "error_code": "GENERAL_ERROR"
            }
    
    def _get_document_context(self, document_type, document_id, file_content=None):
        """
        Gather relevant context about the document for AI analysis
        
        Args:
            document_type: Type of document
            document_id: ID of the document
            file_content: Optional file content
            
        Returns:
            dict: Context information about the document
        """
        context = {
            "document_type": document_type,
            "document_id": document_id,
            "timestamp": datetime.now().isoformat(),
            "raw_content": file_content
        }
        
        if document_type == 'quotation':
            quotation = Quotation.query.get(document_id)
            if quotation:
                context["quotation"] = {
                    "quotation_number": quotation.quotation_number,
                    "date": quotation.quotation_date.isoformat() if quotation.quotation_date else None,
                    "customer": quotation.customer.name if quotation.customer else None,
                    "total_amount": quotation.total_amount,
                    "item_count": len(quotation.items) if quotation.items else 0,
                    "notes": quotation.notes
                }
                
                # Get item summaries (limited to avoid token limits)
                items = []
                for item in quotation.items[:10]:  # Limit to first 10 items
                    items.append({
                        "description": item.description,
                        "scientific_name": item.scientific_name,
                        "quantity": item.quantity,
                        "selling_price": item.selling_price,
                        "supplier": item.supplier
                    })
                context["quotation"]["items"] = items
        
        elif document_type == 'invoice':
            invoice = Invoice.query.get(document_id)
            if invoice:
                context["invoice"] = {
                    "invoice_number": invoice.invoice_number,
                    "date": invoice.invoice_date.isoformat() if invoice.invoice_date else None,
                    "customer": invoice.customer.name if invoice.customer else None,
                    "total_amount": invoice.total_amount,
                    "item_count": len(invoice.items) if invoice.items else 0
                }
                
                # Get item summaries (limited to avoid token limits)
                items = []
                for item in invoice.items[:10]:  # Limit to first 10 items
                    items.append({
                        "description": item.description,
                        "quantity": item.quantity,
                        "price": item.price,
                        "total": item.total
                    })
                context["invoice"]["items"] = items
        
        elif document_type in ['excel', 'pdf']:
            file_upload = FileUpload.query.get(document_id)
            if file_upload:
                context["file_upload"] = {
                    "filename": file_upload.filename,
                    "upload_date": file_upload.upload_date.isoformat() if file_upload.upload_date else None,
                    "file_type": file_upload.file_type,
                    "processed": file_upload.processed,
                    "processing_notes": file_upload.processing_notes,
                    "customer": file_upload.customer.name if file_upload.customer else None
                }
        
        return context
    
    def _analyze_quotation(self, context):
        """
        Analyze a quotation document and provide insights
        
        Args:
            context: Document context information
            
        Returns:
            dict: Insights about the quotation
        """
        try:
            # Validate that quotation information exists in context
            if "quotation" not in context:
                logger.error("Quotation analysis failed: no quotation data in context")
                return {
                    "error": "Quotation information not found",
                    "error_code": "MISSING_QUOTATION_DATA",
                    "resolution": "Ensure the quotation exists and is accessible"
                }
            
            quotation = context["quotation"]
            
            # Validate required fields are present
            required_fields = ['quotation_number', 'date', 'customer', 'total_amount', 'item_count']
            missing_fields = [field for field in required_fields if field not in quotation]
            
            if missing_fields:
                missing_fields_str = ", ".join(missing_fields)
                logger.error(f"Quotation analysis failed: missing required fields: {missing_fields_str}")
                return {
                    "error": f"Quotation data incomplete. Missing fields: {missing_fields_str}",
                    "error_code": "INCOMPLETE_QUOTATION_DATA",
                    "missing_fields": missing_fields
                }
            
            # Check if there are items to analyze
            if not quotation.get('items') or len(quotation.get('items', [])) == 0:
                logger.warning("Quotation has no items to analyze")
                # Still proceed, but include a warning in the context
            
            # Prepare the prompt for analysis
            prompt = f"""
            Analyze this plant nursery quotation information:
            
            Quotation: #{quotation['quotation_number']}
            Date: {quotation['date']}
            Customer: {quotation['customer']}
            Total Amount: {quotation['total_amount']}
            Number of Items: {quotation['item_count']}
            
            Items: 
            {[f"{i+1}. {item['description']} - {item['quantity']} units at {item['selling_price']} each" for i, item in enumerate(quotation.get('items', []))]}
            
            Notes: {quotation.get('notes', 'None')}
            
            Provide brief, specific insights in these categories:
            1. Key Observations (plant variety mix, unusual items, etc.)
            2. Pricing Analysis (identify any pricing outliers)
            3. Business Recommendations (cross-selling opportunities, potential follow-up items)
            
            Keep responses concise and specific to plant nursery business context.
            """
            
            # Log the analysis attempt
            logger.info(f"Analyzing quotation #{quotation['quotation_number']} for customer {quotation['customer']}")
            
            # Get response from OpenAI
            response = self._get_openai_response(prompt)
            
            # Check for errors in the response
            if response and response.startswith("Error:"):
                logger.error(f"OpenAI API error during quotation analysis: {response}")
                return {"error": response, "error_code": "OPENAI_API_ERROR"}
                
            # Format and return the insights
            return self._format_ai_response(response)
            
        except KeyError as ke:
            # Missing expected key in data structure
            error_msg = f"Missing data field during quotation analysis: {str(ke)}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "error_code": "QUOTATION_DATA_STRUCTURE_ERROR"
            }
        except Exception as e:
            # Catch any other errors
            error_msg = f"Error in quotation analysis: {str(e)}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "error_code": "QUOTATION_ANALYSIS_ERROR"
            }
    
    def _analyze_invoice(self, context):
        """
        Analyze an invoice document and provide insights
        
        Args:
            context: Document context information
            
        Returns:
            dict: Insights about the invoice
        """
        try:
            # Validate that invoice information exists in context
            if "invoice" not in context:
                logger.error("Invoice analysis failed: no invoice data in context")
                return {
                    "error": "Invoice information not found",
                    "error_code": "MISSING_INVOICE_DATA",
                    "resolution": "Ensure the invoice exists and is accessible"
                }
            
            invoice = context["invoice"]
            
            # Validate required fields are present
            required_fields = ['invoice_number', 'date', 'customer', 'total_amount', 'item_count']
            missing_fields = [field for field in required_fields if field not in invoice]
            
            if missing_fields:
                missing_fields_str = ", ".join(missing_fields)
                logger.error(f"Invoice analysis failed: missing required fields: {missing_fields_str}")
                return {
                    "error": f"Invoice data incomplete. Missing fields: {missing_fields_str}",
                    "error_code": "INCOMPLETE_INVOICE_DATA",
                    "missing_fields": missing_fields
                }
            
            # Check if there are items to analyze
            if not invoice.get('items') or len(invoice.get('items', [])) == 0:
                logger.warning("Invoice has no items to analyze")
                # Still proceed, but include a warning in the context
            
            # Prepare the prompt for analysis
            prompt = f"""
            Analyze this plant nursery invoice information:
            
            Invoice: #{invoice['invoice_number']}
            Date: {invoice['date']}
            Customer: {invoice['customer']}
            Total Amount: {invoice['total_amount']}
            Number of Items: {invoice['item_count']}
            
            Items: 
            {[f"{i+1}. {item['description']} - {item['quantity']} units at {item['price']} each, total: {item.get('total', 'N/A')}" for i, item in enumerate(invoice.get('items', []))]}
            
            Provide brief, specific insights in these categories:
            1. Key Observations (unusual patterns, seasonal trends)
            2. Customer Purchasing Patterns
            3. Business Recommendations (inventory, future orders)
            
            Keep responses concise and specific to plant nursery business context.
            """
            
            # Log the analysis attempt
            logger.info(f"Analyzing invoice #{invoice['invoice_number']} for customer {invoice['customer']}")
            
            # Get response from OpenAI
            response = self._get_openai_response(prompt)
            
            # Check for errors in the response
            if response and response.startswith("Error:"):
                logger.error(f"OpenAI API error during invoice analysis: {response}")
                return {"error": response, "error_code": "OPENAI_API_ERROR"}
                
            # Format and return the insights
            return self._format_ai_response(response)
            
        except KeyError as ke:
            # Missing expected key in data structure
            error_msg = f"Missing data field during invoice analysis: {str(ke)}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "error_code": "INVOICE_DATA_STRUCTURE_ERROR"
            }
        except Exception as e:
            # Catch any other errors
            error_msg = f"Error in invoice analysis: {str(e)}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "error_code": "INVOICE_ANALYSIS_ERROR"
            }
    
    def _analyze_excel(self, context):
        """
        Analyze an Excel file and provide insights
        
        Args:
            context: Document context information
            
        Returns:
            dict: Insights about the Excel file
        """
        try:
            # Validate that file upload information exists in context
            if "file_upload" not in context:
                logger.error("Excel analysis failed: no file upload data in context")
                return {
                    "error": "File upload information not found",
                    "error_code": "MISSING_FILE_UPLOAD_DATA",
                    "resolution": "Ensure the file upload record exists"
                }
            
            file_upload = context["file_upload"]
            raw_content = context.get("raw_content", "Content not available")
            
            # Validate required fields are present
            required_fields = ['filename', 'file_type', 'upload_date']
            missing_fields = [field for field in required_fields if field not in file_upload]
            
            if missing_fields:
                missing_fields_str = ", ".join(missing_fields)
                logger.error(f"Excel analysis failed: missing required fields: {missing_fields_str}")
                return {
                    "error": f"Excel file data incomplete. Missing fields: {missing_fields_str}",
                    "error_code": "INCOMPLETE_EXCEL_FILE_DATA",
                    "missing_fields": missing_fields
                }
            
            # Validate file type is actually Excel
            if file_upload['file_type'].lower() != 'excel':
                error_msg = f"File is not an Excel file. Type: {file_upload['file_type']}"
                logger.error(error_msg)
                return {
                    "error": error_msg,
                    "error_code": "INVALID_FILE_TYPE",
                    "expected": "excel",
                    "actual": file_upload['file_type']
                }
            
            # Prepare the prompt for analysis
            prompt = f"""
            Analyze this plant nursery Excel file information:
            
            Filename: {file_upload['filename']}
            Type: {file_upload['file_type']}
            Customer: {file_upload.get('customer', 'Unknown')}
            Upload Date: {file_upload['upload_date']}
            Processed: {file_upload.get('processed', 'Unknown')}
            Processing Notes: {file_upload.get('processing_notes', 'None')}
            
            Provide brief, specific insights in these categories:
            1. Data Quality Assessment
            2. Potential Plant Inventory Insights
            3. Pricing Pattern Observations
            
            Keep responses concise and specific to plant nursery business context.
            """
            
            # Log the analysis attempt
            logger.info(f"Analyzing Excel file: {file_upload['filename']}")
            
            # Get response from OpenAI
            response = self._get_openai_response(prompt)
            
            # Check for errors in the response
            if response and response.startswith("Error:"):
                logger.error(f"OpenAI API error during Excel analysis: {response}")
                return {"error": response, "error_code": "OPENAI_API_ERROR"}
                
            # Format and return the insights
            return self._format_ai_response(response)
            
        except KeyError as ke:
            # Missing expected key in data structure
            error_msg = f"Missing data field during Excel analysis: {str(ke)}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "error_code": "EXCEL_DATA_STRUCTURE_ERROR"
            }
        except Exception as e:
            # Catch any other errors
            error_msg = f"Error in Excel file analysis: {str(e)}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "error_code": "EXCEL_ANALYSIS_ERROR"
            }
    
    def _analyze_pdf(self, context):
        """
        Analyze a PDF file and provide insights
        
        Args:
            context: Document context information
            
        Returns:
            dict: Insights about the PDF file
        """
        try:
            # Validate that file upload information exists in context
            if "file_upload" not in context:
                logger.error("PDF analysis failed: no file upload data in context")
                return {
                    "error": "File upload information not found",
                    "error_code": "MISSING_FILE_UPLOAD_DATA",
                    "resolution": "Ensure the file upload record exists"
                }
            
            file_upload = context["file_upload"]
            raw_content = context.get("raw_content", "Content not available")
            
            # Validate required fields are present
            required_fields = ['filename', 'file_type', 'upload_date']
            missing_fields = [field for field in required_fields if field not in file_upload]
            
            if missing_fields:
                missing_fields_str = ", ".join(missing_fields)
                logger.error(f"PDF analysis failed: missing required fields: {missing_fields_str}")
                return {
                    "error": f"PDF file data incomplete. Missing fields: {missing_fields_str}",
                    "error_code": "INCOMPLETE_PDF_FILE_DATA",
                    "missing_fields": missing_fields
                }
            
            # Validate file type is actually PDF
            if file_upload['file_type'].lower() != 'pdf':
                error_msg = f"File is not a PDF file. Type: {file_upload['file_type']}"
                logger.error(error_msg)
                return {
                    "error": error_msg,
                    "error_code": "INVALID_FILE_TYPE",
                    "expected": "pdf",
                    "actual": file_upload['file_type']
                }
            
            # Check if we have any raw content for better analysis
            if raw_content == "Content not available" or not raw_content:
                logger.warning(f"PDF analysis for {file_upload['filename']} has no raw content available")
                # We'll still continue with the analysis using available metadata
            
            # Prepare the prompt for analysis
            prompt = f"""
            Analyze this plant nursery PDF document information:
            
            Filename: {file_upload['filename']}
            Type: {file_upload['file_type']}
            Customer: {file_upload.get('customer', 'Unknown')}
            Upload Date: {file_upload['upload_date']}
            Processed: {file_upload.get('processed', 'Unknown')}
            Processing Notes: {file_upload.get('processing_notes', 'None')}
            
            Provide brief, specific insights in these categories:
            1. Document Purpose Assessment
            2. Key Information Extracted
            3. Suggested Actions Based on Content
            
            Keep responses concise and specific to plant nursery business context.
            """
            
            # Log the analysis attempt
            logger.info(f"Analyzing PDF file: {file_upload['filename']}")
            
            # Get response from OpenAI
            response = self._get_openai_response(prompt)
            
            # Check for errors in the response
            if response and response.startswith("Error:"):
                logger.error(f"OpenAI API error during PDF analysis: {response}")
                return {"error": response, "error_code": "OPENAI_API_ERROR"}
                
            # Format and return the insights
            return self._format_ai_response(response)
            
        except KeyError as ke:
            # Missing expected key in data structure
            error_msg = f"Missing data field during PDF analysis: {str(ke)}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "error_code": "PDF_DATA_STRUCTURE_ERROR"
            }
        except Exception as e:
            # Catch any other errors
            error_msg = f"Error in PDF file analysis: {str(e)}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "error_code": "PDF_ANALYSIS_ERROR"
            }
    
    def _get_openai_response(self, prompt):
        """
        Send a prompt to OpenAI API and get a response
        
        Args:
            prompt: The prompt to send to OpenAI
            
        Returns:
            str: The response from OpenAI
        """
        if not self.client:
            logger.error("OpenAI client not initialized - missing API key")
            return "Error: OpenAI API key is missing. Please configure it in the settings."
            
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a horticultural business analyst specializing in plant nursery operations, pricing, and inventory management. Provide concise, actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3,  # Lower temperature for more focused responses
            )
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return f"Error generating insights: {str(e)}"
    
    def _format_ai_response(self, response):
        """
        Format the AI response into a structured insights object
        
        Args:
            response: Raw response from OpenAI
            
        Returns:
            dict: Structured insights
        """
        # Simple formatting - split by numbered sections
        sections = {}
        current_section = "overview"
        sections[current_section] = []
        
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check if line starts with a number followed by a period (e.g., "1. Key Observations")
            if line[0].isdigit() and ". " in line[:5]:
                # Extract section title
                title_start = line.find(". ") + 2
                current_section = line[title_start:].lower().replace(" ", "_")
                sections[current_section] = []
            else:
                sections[current_section].append(line)
        
        # Convert lists to strings
        insights = {}
        for section, lines in sections.items():
            insights[section] = "\n".join(lines)
        
        return {
            "insights": insights,
            "timestamp": datetime.now().isoformat(),
            "raw_response": response
        }