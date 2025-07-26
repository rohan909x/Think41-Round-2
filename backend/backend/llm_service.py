import os
import json
from typing import List, Dict, Any, Optional
from groq import Groq
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama3-8b-8192"  # Using Llama 3 model
        
    def get_system_prompt(self) -> str:
        """Get the system prompt for the chatbot"""
        return """You are a helpful customer support assistant for an e-commerce clothing website. 
        You have access to a database with information about products, orders, inventory, and users.
        
        Your capabilities include:
        1. Answering questions about products (availability, pricing, categories, brands)
        2. Checking order status and tracking information
        3. Providing information about user accounts and order history
        4. Helping with general customer service inquiries
        
        Always be polite, helpful, and professional. If you need more information to help a customer, 
        ask clarifying questions. If you can't find specific information in the database, let the customer 
        know and suggest alternative ways to get help.
        
        When querying the database, use the provided functions to get accurate information."""
    
    def query_database(self, db: Session, query_type: str, **kwargs) -> List[Dict[str, Any]]:
        """Query the database based on the type of information needed"""
        try:
            if query_type == "product_search":
                return self._search_products(db, **kwargs)
            elif query_type == "order_status":
                return self._get_order_status(db, **kwargs)
            elif query_type == "user_orders":
                return self._get_user_orders(db, **kwargs)
            elif query_type == "inventory_check":
                return self._check_inventory(db, **kwargs)
            elif query_type == "top_products":
                return self._get_top_products(db, **kwargs)
            else:
                return []
        except Exception as e:
            print(f"Database query error: {e}")
            return []
    
    def _search_products(self, db: Session, category: str = None, brand: str = None, 
                        department: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for products based on criteria"""
        query = """
        SELECT p.id, p.name, p.brand, p.category, p.department, p.retail_price, p.sku,
               COUNT(ii.id) as available_inventory
        FROM products p
        LEFT JOIN inventory_items ii ON p.id = ii.product_id AND ii.sold_at IS NULL
        WHERE 1=1
        """
        params = {}
        
        if category:
            query += " AND p.category ILIKE :category"
            params['category'] = f"%{category}%"
        if brand:
            query += " AND p.brand ILIKE :brand"
            params['brand'] = f"%{brand}%"
        if department:
            query += " AND p.department ILIKE :department"
            params['department'] = f"%{department}%"
            
        query += " GROUP BY p.id, p.name, p.brand, p.category, p.department, p.retail_price, p.sku"
        query += " ORDER BY available_inventory DESC"
        query += f" LIMIT {limit}"
        
        result = db.execute(text(query), params)
        return [dict(row) for row in result]
    
    def _get_order_status(self, db: Session, order_id: int = None, user_id: int = None) -> List[Dict[str, Any]]:
        """Get order status information"""
        if order_id:
            query = """
            SELECT o.order_id, o.status, o.created_at, o.shipped_at, o.delivered_at, o.returned_at,
                   o.num_of_item, u.first_name, u.last_name, u.email
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.order_id = :order_id
            """
            result = db.execute(text(query), {"order_id": order_id})
        elif user_id:
            query = """
            SELECT o.order_id, o.status, o.created_at, o.shipped_at, o.delivered_at, o.returned_at,
                   o.num_of_item
            FROM orders o
            WHERE o.user_id = :user_id
            ORDER BY o.created_at DESC
            LIMIT 10
            """
            result = db.execute(text(query), {"user_id": user_id})
        else:
            return []
        
        return [dict(row) for row in result]
    
    def _get_user_orders(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """Get all orders for a specific user"""
        query = """
        SELECT o.order_id, o.status, o.created_at, o.num_of_item,
               COUNT(oi.id) as total_items,
               SUM(p.retail_price) as total_value
        FROM orders o
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        LEFT JOIN products p ON oi.product_id = p.id
        WHERE o.user_id = :user_id
        GROUP BY o.order_id, o.status, o.created_at, o.num_of_item
        ORDER BY o.created_at DESC
        """
        result = db.execute(text(query), {"user_id": user_id})
        return [dict(row) for row in result]
    
    def _check_inventory(self, db: Session, product_id: int = None, sku: str = None) -> List[Dict[str, Any]]:
        """Check inventory availability"""
        if product_id:
            query = """
            SELECT p.id, p.name, p.sku, p.retail_price,
                   COUNT(ii.id) as available_items
            FROM products p
            LEFT JOIN inventory_items ii ON p.id = ii.product_id AND ii.sold_at IS NULL
            WHERE p.id = :product_id
            GROUP BY p.id, p.name, p.sku, p.retail_price
            """
            result = db.execute(text(query), {"product_id": product_id})
        elif sku:
            query = """
            SELECT p.id, p.name, p.sku, p.retail_price,
                   COUNT(ii.id) as available_items
            FROM products p
            LEFT JOIN inventory_items ii ON p.id = ii.product_id AND ii.sold_at IS NULL
            WHERE p.sku = :sku
            GROUP BY p.id, p.name, p.sku, p.retail_price
            """
            result = db.execute(text(query), {"sku": sku})
        else:
            return []
        
        return [dict(row) for row in result]
    
    def _get_top_products(self, db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top selling products"""
        query = """
        SELECT p.id, p.name, p.brand, p.category, p.retail_price,
               COUNT(oi.id) as total_sales,
               COUNT(ii.id) as available_inventory
        FROM products p
        LEFT JOIN order_items oi ON p.id = oi.product_id
        LEFT JOIN inventory_items ii ON p.id = ii.product_id AND ii.sold_at IS NULL
        GROUP BY p.id, p.name, p.brand, p.category, p.retail_price
        ORDER BY total_sales DESC
        LIMIT :limit
        """
        result = db.execute(text(query), {"limit": limit})
        return [dict(row) for row in result]
    
    def generate_response(self, db: Session, user_message: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Generate a response using the LLM with database context"""
        
        # Analyze the user message to determine what information is needed
        analysis_prompt = f"""
        Analyze this customer message and determine what type of information is needed:
        "{user_message}"
        
        Choose from these categories:
        1. product_search - Customer is asking about products, categories, brands, or availability
        2. order_status - Customer is asking about order status, tracking, or delivery
        3. user_orders - Customer is asking about their order history
        4. inventory_check - Customer is asking about specific product availability
        5. top_products - Customer is asking about popular or trending products
        6. general_help - General customer service question
        
        Respond with just the category name.
        """
        
        try:
            analysis_response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=50,
                temperature=0.1
            )
            
            query_type = analysis_response.choices[0].message.content.strip().lower()
            
            # Extract relevant information from the message
            extracted_info = self._extract_info_from_message(user_message)
            
            # Query the database if needed
            db_results = []
            if query_type != "general_help":
                db_results = self.query_database(db, query_type, **extracted_info)
            
            # Build the context for the LLM
            context = self._build_context(query_type, db_results, extracted_info)
            
            # Generate the response
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": f"Context: {context}\n\nCustomer message: {user_message}"}
            ]
            
            if conversation_history:
                for msg in conversation_history[-5:]:  # Include last 5 messages for context
                    messages.append({"role": msg["role"], "content": msg["content"]})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again later or contact our support team."
    
    def _extract_info_from_message(self, message: str) -> Dict[str, Any]:
        """Extract relevant information from the user message"""
        # This is a simplified extraction - in a real system, you might use NER or more sophisticated parsing
        message_lower = message.lower()
        extracted = {}
        
        # Extract potential order IDs
        import re
        order_matches = re.findall(r'order[:\s]*#?(\d+)', message_lower)
        if order_matches:
            extracted['order_id'] = int(order_matches[0])
        
        # Extract potential user IDs
        user_matches = re.findall(r'user[:\s]*#?(\d+)', message_lower)
        if user_matches:
            extracted['user_id'] = int(user_matches[0])
        
        # Extract product categories
        categories = ['shirts', 'pants', 'dresses', 'shoes', 'accessories', 'jackets', 'sweaters']
        for category in categories:
            if category in message_lower:
                extracted['category'] = category
                break
        
        # Extract brands (simplified)
        brands = ['nike', 'adidas', 'puma', 'levi', 'calvin', 'ralph']
        for brand in brands:
            if brand in message_lower:
                extracted['brand'] = brand
                break
        
        return extracted
    
    def _build_context(self, query_type: str, db_results: List[Dict[str, Any]], extracted_info: Dict[str, Any]) -> str:
        """Build context string for the LLM based on database results"""
        if not db_results:
            return "No specific information found in the database for this query."
        
        context_parts = []
        
        if query_type == "product_search":
            context_parts.append("Available products:")
            for product in db_results[:5]:  # Limit to 5 products
                context_parts.append(f"- {product['name']} by {product['brand']} ({product['category']}) - ${product['retail_price']} - {product['available_inventory']} in stock")
        
        elif query_type == "order_status":
            context_parts.append("Order information:")
            for order in db_results:
                context_parts.append(f"Order #{order['order_id']}: {order['status']} - Created: {order['created_at']}")
                if order.get('shipped_at'):
                    context_parts.append(f"  Shipped: {order['shipped_at']}")
                if order.get('delivered_at'):
                    context_parts.append(f"  Delivered: {order['delivered_at']}")
        
        elif query_type == "user_orders":
            context_parts.append("User's order history:")
            for order in db_results[:5]:
                context_parts.append(f"Order #{order['order_id']}: {order['status']} - {order['total_items']} items - ${order.get('total_value', 0):.2f}")
        
        elif query_type == "inventory_check":
            context_parts.append("Inventory information:")
            for item in db_results:
                context_parts.append(f"{item['name']} (SKU: {item['sku']}): {item['available_items']} available - ${item['retail_price']}")
        
        elif query_type == "top_products":
            context_parts.append("Top selling products:")
            for product in db_results[:5]:
                context_parts.append(f"{product['name']} by {product['brand']}: {product['total_sales']} sold - {product['available_inventory']} in stock")
        
        return "\n".join(context_parts) 