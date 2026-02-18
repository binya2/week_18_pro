import logging
import re
from typing import Dict, List, Any
from datetime import datetime
from shared.models import PizzaOrders, PizzaAnalysis, Status
from shared.utils.caching import cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnrichmentService:

    @staticmethod
    async def get_analysis_rules() -> Dict[str, List[str]]:
        rules = await PizzaAnalysis.find_one()
        if not rules:
            return {}

        return {
            "common_allergens": rules.common_allergens,
            "forbidden_non_kosher": rules.forbidden_non_kosher,
            "meat_ingredients": rules.meat_ingredients,
            "dairy_ingredients": rules.dairy_ingredients
        }

    @staticmethod
    @cache(expire=60)
    async def analyze_text(text: str, rules: Dict[str, List[str]]) -> Dict[str, Any]:
        try:
            text = text.lower()
            report = {}

            for category, keywords in rules.items():
                found = []
                for keyword in keywords:
                    pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                    if re.search(pattern, text):
                        found.append(keyword.lower())
                if found:
                    report[category] = found
            return report
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return {}

    @staticmethod
    async def process_pizza(order_data: dict):
        order_id = order_data.get('order_id')
        recipe_text = order_data.get('recipes', "")

        rules = await EnrichmentService.get_analysis_rules()
        if not rules:
            logger.warning("No analysis rules found!")
            return None

        result = await EnrichmentService.analyze_text(recipe_text, rules)
        if not result:
            logger.info(f"Skipping order {order_id}: Analysis returned no result.")
            return None
        analysis_result = result["data"]

        order = await PizzaOrders.find_one(PizzaOrders.order_id == order_id)
        if not order:
            logger.info(f"Order {order_id} not found in database.")
            return None

        has_meat = bool(analysis_result.get("meat_ingredients"))
        has_dairy = bool(analysis_result.get("dairy_ingredients"))
        has_forbidden = bool(analysis_result.get("forbidden_non_kosher"))

        order.is_meat = has_meat
        order.is_dairy = has_dairy

        order.updated_by = result['source']
        order.insert_date = datetime.now()

        is_kosher = True
        if has_forbidden:
            is_kosher = False
        elif has_meat and has_dairy:
            is_kosher = False

        if is_kosher:
            order.status = Status.DELIVERED
        else:
            order.status = Status.BURNT

        logger.info(f"Order {order_id} updated with status {order.status.name}.")

        await order.save()
        return {
            "order_id": order_id,
            "special_instructions": order_data.get('special_instructions_cleaned'),
            "common_allergens": analysis_result.get("common_allergens"),
        }

