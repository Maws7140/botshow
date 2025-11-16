"""
Filtering module for products based on price, category, etc.
"""
from typing import Optional, List


class ProductFilter:
    """Filters products based on various criteria."""

    def __init__(self, min_price: float = 0, max_price: float = 999999,
                 categories: List[str] = None, excluded_categories: List[str] = None):
        """
        Initialize product filter.

        Args:
            min_price: Minimum price threshold
            max_price: Maximum price threshold
            categories: List of categories to include (None = all)
            excluded_categories: List of categories to exclude
        """
        self.min_price = min_price
        self.max_price = max_price
        self.categories = [c.lower() for c in categories] if categories else None
        self.excluded_categories = [c.lower() for c in excluded_categories] if excluded_categories else []

    def should_process_product(self, price: Optional[float], category: Optional[str]) -> bool:
        """
        Determine if a product should be processed based on filters.

        Args:
            price: Product price
            category: Product category

        Returns:
            True if product passes filters, False otherwise
        """
        # Check price range
        if price is not None:
            if price < self.min_price or price > self.max_price:
                return False

        # Check category
        if category:
            category = category.lower()

            # Check excluded categories
            if category in self.excluded_categories:
                return False

            # Check included categories (if specified)
            if self.categories is not None:
                if category not in self.categories:
                    return False

        return True

    def update_price_range(self, min_price: float, max_price: float):
        """Update price range filter."""
        self.min_price = min_price
        self.max_price = max_price

    def update_categories(self, categories: List[str]):
        """Update categories filter."""
        self.categories = [c.lower() for c in categories] if categories else None

    def add_excluded_category(self, category: str):
        """Add a category to the exclusion list."""
        if category.lower() not in self.excluded_categories:
            self.excluded_categories.append(category.lower())

    def remove_excluded_category(self, category: str):
        """Remove a category from the exclusion list."""
        category = category.lower()
        if category in self.excluded_categories:
            self.excluded_categories.remove(category)

    def get_filter_summary(self) -> str:
        """Get a summary of current filters."""
        lines = [
            f"Price range: €{self.min_price} - €{self.max_price}",
        ]

        if self.categories:
            lines.append(f"Include categories: {', '.join(self.categories)}")
        else:
            lines.append("Include categories: All")

        if self.excluded_categories:
            lines.append(f"Exclude categories: {', '.join(self.excluded_categories)}")

        return '\n'.join(lines)
