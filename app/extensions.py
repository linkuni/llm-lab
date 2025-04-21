import boto3
import spacy

# Initialize global variables
nlp = None
bedrock_runtime = None

def init_extensions(app):
    """Initialize Flask extensions and other services"""
    global nlp, bedrock_runtime
    
    # Initialize spaCy
    nlp = spacy.load("en_core_web_sm")
    
    # Initialize AWS Bedrock client
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name=app.config["AWS_REGION"],
        aws_access_key_id=app.config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=app.config["AWS_SECRET_ACCESS_KEY"]
    )
    
    return nlp, bedrock_runtime

def get_nlp():
    """Get the spaCy NLP instance"""
    global nlp
    return nlp

def get_bedrock_client():
    """Get the AWS Bedrock client"""
    global bedrock_runtime
    return bedrock_runtime 