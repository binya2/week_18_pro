import re
from typing import Dict, List, Any

from shared.models import PizzaOrders, PizzaAnalysis, Status
from shared.utils.caching import cache


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
    def analyze_text(text: str, rules: Dict[str, List[str]]) -> Dict[str, List[str]]:
        text = text.lower()
        report = {}

        for category, keywords in rules.items():
            found = []
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, text):
                    found.append(keyword)
            if found:
                report[category] = found
        return report

    @staticmethod
    async def process_pizza(order_data: dict):
        order_id = order_data.get('order_id')
        recipe_text = order_data.get('recipes', "")

        rules = await EnrichmentService.get_analysis_rules()
        if not rules:
            print("No analysis rules found!")
            return

        analysis_result = EnrichmentService.analyze_text(recipe_text, rules)

        order = await PizzaOrders.find_one(PizzaOrders.order_id == order_id)
        if not order:
            return

        has_meat = bool(analysis_result.get("meat_ingredients"))
        has_dairy = bool(analysis_result.get("dairy_ingredients"))
        has_forbidden = bool(analysis_result.get("forbidden_non_kosher"))

        order.is_meat = has_meat
        order.is_dairy = has_dairy

        is_kosher = True
        if has_forbidden:
            is_kosher = False
        elif has_meat and has_dairy:
            is_kosher = False

        if is_kosher:
            order.status = Status.DELIVERED
        else:
            order.status = Status.BURNT

        order.allergies_flagged = bool(analysis_result.get("common_allergens"))
        await order.save()