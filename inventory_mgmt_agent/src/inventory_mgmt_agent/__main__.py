from .database import initialize_and_populate_db
from .agents import InventoryAgent
import logging
import schedule
import time
from dotenv import load_dotenv

load_dotenv()

def run_inventory_check():

    logger = logging.getLogger('ecommerceagent')
    logger.info("Starting scheduled inventory check")
    agent = InventoryAgent()
    check_result = agent.check_inventory()
    logger.info(f"Inventory check completed: {len(check_result.get('actions_taken', []))} actions taken")
  
print("Hello from Siva Agent")
initialize_and_populate_db()

run_inventory_check()

schedule.every(24).hours.do(run_inventory_check)

while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute for scheduled tasks
        except KeyboardInterrupt:           
            break
        except Exception as e:         
            time.sleep(300)