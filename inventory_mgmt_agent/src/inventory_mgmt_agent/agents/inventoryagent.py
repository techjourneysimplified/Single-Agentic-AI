import uuid
import logging
from langchain_openai import ChatOpenAI
from langchain_experimental.tools import PythonREPLTool
from langchain_community.tools.gmail import GmailSendMessage

from langchain.agents import AgentExecutor,create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate,MessagesPlaceholder

from ..tools import get_gmail_service,get_sql_toolkit
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class InventoryAgent:

    def __init__(self,model_name: str = "gpt-4o-mini"):
           self.llm= ChatOpenAI(model=model_name)
           self.gmail_service= get_gmail_service()
           self.setup_logging()
           self.tools=self._setup_tools()
           self.agent_executor= self._create_agent()
    
    
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('inventory_agent.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('InventoryAgent')

    def _setup_tools(self):

            """Setup all tools that the agent will use"""
            sql_toolkit = get_sql_toolkit(self.llm)
            python_repl = PythonREPLTool()

            # Define custom tools with clear descriptions and structured args
            tools = [

                GmailSendMessage(api_resource=self.gmail_service),
               # calculate_reorder_quantity,
                #calculate_sales_metrics,
                python_repl
            ]

            # Add SQL tools with their descriptions
            tools.extend(sql_toolkit.get_tools())

            return tools
    
    def _create_agent(self) -> AgentExecutor:

        """Create the agent with a custom prompt using OpenAI functions"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an autonomous Inventory Management AI Agent responsible for optimizing inventory levels and managing purchase orders efficiently.

            Core Responsibilities:
            1. Monitor stock levels and trigger reorders at appropriate thresholds
            2. Analyze sales data to optimize inventory levels
            3. Generate and manage purchase orders
            4. Communicate with suppliers via email

            Mandatory Rules:
            1. NEVER make assumptions - verify all data with appropriate tools
            2. Check table schemas before any database queries
            3. Use python_repl only for complex calculations not possible with other tools
            4. Document all calculations with clear comments and variable names
            5. Implement error handling with alternative approaches
            6. Validate all data before decision-making

            Inventory Parameters:
            - Safety Stock = Average Daily Sales × 3 days
            - Target Stock = Average Daily Sales × 7 days
            - Reorder Point = Safety Stock Level
            - Reorder Quantity = Target Stock + Safety Stock - Current Stock
            - Reorder Trigger: Current Stock ≤ Reorder Point

            Database Guidelines:
            1. Verify schema before queries
            2. Use appropriate aggregation functions instead of querying for all data and then filtering or aggregating.
            3. Implement proper table joins
            4.  Use a single insert statement to insert all the purchase order details.
            5. Maintain data consistency and validation

            Analysis Process:
            1. Stock Level Assessment
                - Compare current levels to reorder points
                - Check 30-day sales history
                - Calculate: daily sales average, velocity, turnover

            2. Purchase Order Management
                - Calculate optimal quantities
                - Group by supplier
                - Update database records
                - Send supplier communications.
                - If 2 or more products are ordered from the same supplier, then send a single email to the supplier.


            Email Template Structure:
            Subject: Purchase Order #[PO_NUMBER] - [COMPANY_NAME]

            # Purchase Order

            Dear [SUPPLIER_NAME],

            I hope this email finds you well. We would like to place the following purchase order:

            ## Purchase Order Details
            - **PO Number:** [PO_NUMBER]
            - **Order Date:** [DATE]
            - **Expected Delivery:** [DELIVERY_DATE]

            ## Order Items
            1. **[PRODUCT_NAME]**
               - Quantity: [QUANTITY]
               - Unit Price: [PRICE]
               - Total: [TOTAL]
            [Repeat for each item]

            **Total Order Value:** [GRAND_TOTAL]

            Please confirm receipt of this order and expected delivery date. If you have any questions or concerns, please don't hesitate to contact us.

            Best regards,
            [COMPANY_NAME]
            [CONTACT_DETAILS]

            Current date and time: {current_time}

            Best Practices:
            1. Use structured, logical thinking
            2. Generate complete, well-thought-out code in one pass
            3. Show detailed calculations
            4. Document all decisions with clear reasoning
            5. Validate results before actions
            6. Maintain professional communication"""),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=25,
            handle_parsing_errors=True
        )
    
    def check_inventory(self) -> Dict:
         
        self.logger.info("Starting inventory check")

        query = """
            IMPORTANT: Follow these steps precisely:
            1. Verify all data using appropriate tools
            2. Show detailed calculations with python_repl
            3. Document your reasoning and decision process
            4. Validate results before taking actions
            5. Update database records as needed
            6. Generate clear, actionable outputs

            Note: When using sql_db_query tool, provide the SQL query directly without additional markdown formatting.
            if Action is sql_db_query, then dont use ```sql in the Action Input.
            When using python_repl tool, provide the python code directly without additional markdown formatting.

            Task:

            Perform the following tasks:
                1. Check for low stock products. Every product has a reorder threshold.
                2. For each low stock product:
                   - Analyze its sales metrics for past 7 days
                   - Review historical sales data
                   - Calculate optimal reorder quantity
                3. Provide a summary of all actions taken
                4. Create a purchase order for the low stock products and update the  Purchase_Order table in the database.
                5. Send email to supplier

            """

        result = self.agent_executor.invoke(
                input={
                    "input": query,
                    "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )

        # Validate result
        if not result.get('output'):
            raise ValueError("Agent returned empty result")

        self.logger.info("Agent execution completed successfully")
        return result
         
