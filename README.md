# E-commerce Customer Support Chatbot Backend

A FastAPI-based backend for a customer support chatbot designed for an e-commerce clothing website. The chatbot can answer questions about products, orders, inventory, and provide general customer support.

## Features

- **Product Information**: Search and provide details about clothing products, categories, brands, and availability
- **Order Tracking**: Check order status, delivery information, and order history
- **Inventory Management**: Check product availability and stock levels
- **User Support**: Handle general customer service inquiries
- **Conversation Management**: Maintain chat sessions with conversation history
- **LLM Integration**: Powered by Groq LLM API for intelligent responses

## Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **LLM**: Groq API (Llama 3 model)
- **Data Processing**: Pandas for CSV data ingestion

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application and endpoints
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   └── llm_service.py       # LLM integration and business logic
├── scripts/
│   ├── __init__.py
│   └── load_data.py         # CSV data ingestion script
├── requirements.txt         # Python dependencies
├── run.py                  # Application startup script
├── env_example.txt         # Environment variables template
└── README.md               # This file
```

## Setup Instructions

### Step 1: Environment Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   - Copy `env_example.txt` to `.env`
   - Update the following variables:
     ```
     DATABASE_URL=postgresql://username:password@localhost:5432/ecommerce_chatbot
     GROQ_API_KEY=your_groq_api_key_here
     SECRET_KEY=your_secret_key_here
     ```

3. **Set up PostgreSQL database**:
   - Create a PostgreSQL database named `ecommerce_chatbot`
   - Update the `DATABASE_URL` in your `.env` file

### Step 2: Data Ingestion

1. **Extract CSV files** (if not already done):
   ```bash
   # The CSV files should be in: C:\Users\rohan\Downloads\archive\archive\
   ```

2. **Load data into database**:
   ```bash
   python scripts/load_data.py
   ```

### Step 3: Start the Application

1. **Run the FastAPI server**:
   ```bash
   python run.py
   ```

2. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/health
   - Root Endpoint: http://localhost:8000/

## API Endpoints

### Chat Endpoints

- `POST /api/chat` - Send a message and get AI response
- `GET /api/sessions/{session_id}` - Get a specific chat session
- `GET /api/sessions` - List chat sessions
- `DELETE /api/sessions/{session_id}` - Delete a chat session

### Example Usage

#### Start a Chat Session

```bash
curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What products do you have in the shirts category?",
       "user_id": 1
     }'
```

#### Continue a Chat Session

```bash
curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What about Nike shoes?",
       "session_id": "your-session-id-here"
     }'
```

#### Check Order Status

```bash
curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What is the status of order #12345?",
       "user_id": 1
     }'
```

## Database Schema

The application uses the following main tables:

- **users**: Customer information
- **products**: Product catalog
- **inventory_items**: Stock management
- **orders**: Order information
- **order_items**: Individual items in orders
- **distribution_centers**: Warehouse locations
- **chat_sessions**: Chat conversation sessions
- **chat_messages**: Individual messages in conversations

## LLM Integration

The chatbot uses Groq's LLM API with the following capabilities:

1. **Message Analysis**: Automatically determines the type of customer inquiry
2. **Database Queries**: Retrieves relevant information from the database
3. **Context Building**: Combines database results with conversation history
4. **Response Generation**: Creates helpful, contextual responses

### Supported Query Types

- `product_search`: Find products by category, brand, or department
- `order_status`: Check order status and tracking
- `user_orders`: Get user's order history
- `inventory_check`: Check product availability
- `top_products`: Get popular products
- `general_help`: General customer service

## Development

### Adding New Features

1. **New Database Queries**: Add methods to `LLMService` class
2. **New API Endpoints**: Add routes to `main.py`
3. **New Data Models**: Add models to `models.py` and schemas to `schemas.py`

### Testing

The API includes automatic documentation at `/docs` where you can:
- View all available endpoints
- Test API calls directly
- See request/response schemas

## Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Check PostgreSQL is running
   - Verify `DATABASE_URL` in `.env` file
   - Ensure database exists

2. **LLM API Error**:
   - Verify `GROQ_API_KEY` is set correctly
   - Check internet connection
   - Ensure API key has sufficient credits

3. **Data Loading Issues**:
   - Check CSV file paths in `load_data.py`
   - Ensure CSV files are not corrupted
   - Verify database permissions

### Logs

Check the console output for detailed error messages and debugging information.

## Production Deployment

For production deployment, consider:

1. **Environment Variables**: Use proper secret management
2. **Database**: Use managed PostgreSQL service
3. **API Keys**: Secure storage for LLM API keys
4. **CORS**: Configure allowed origins properly
5. **Logging**: Implement proper logging
6. **Monitoring**: Add health checks and monitoring

## License

This project is for educational purposes. Please ensure compliance with Groq's API terms of service and any applicable data protection regulations. 