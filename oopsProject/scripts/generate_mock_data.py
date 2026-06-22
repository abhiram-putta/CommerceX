"""
Generate realistic mock data for sMart backend.
This creates users, products, categories, orders, reviews, and interactions.
"""
import asyncio
import random
from datetime import datetime, timedelta
from typing import List
from uuid import UUID

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.category import Category
from app.models.product import Product
from app.models.user import User, UserProfile
from app.models.inventory import Inventory
from app.models.cart import Cart
from app.models.order import Order, OrderItem, OrderTracking
from app.models.payment import Payment
from app.models.review import Review
from app.models.interaction import UserInteraction
from app.models.analytics import SearchQuery
from app.models.notification import Notification
from app.utils.enums import (
    UserRole, OrderStatus, OrderType, PaymentStatus,
    PaymentMethod, InteractionType, NotificationType, OwnerType
)
from app.utils.helpers import generate_order_number, slugify

fake = Faker(['en_IN'])  # Indian locale for realistic data


class MockDataGenerator:
    """Generate realistic mock data for the system."""

    def __init__(self):
        self.users: List[User] = []
        self.categories: List[Category] = []
        self.products: List[Product] = []
        self.customers: List[User] = []
        self.retailers: List[User] = []
        self.wholesalers: List[User] = []

    async def generate_all(self, db: AsyncSession):
        """Generate all mock data."""
        print("🚀 Starting mock data generation...")

        await self.generate_categories(db)
        print("✅ Generated categories")

        await self.generate_users(db)
        print("✅ Generated users")

        await self.generate_products(db)
        print("✅ Generated products")

        await self.generate_inventory(db)
        print("✅ Generated inventory")

        await self.generate_orders(db)
        print("✅ Generated orders")

        await self.generate_reviews(db)
        print("✅ Generated reviews")

        await self.generate_interactions(db)
        print("✅ Generated user interactions")

        await self.generate_search_queries(db)
        print("✅ Generated search queries")

        await self.generate_notifications(db)
        print("✅ Generated notifications")

        print("🎉 Mock data generation complete!")

    async def generate_categories(self, db: AsyncSession):
        """Generate product categories with hierarchy."""
        # Root categories
        root_categories = [
            ("Electronics", "electronics", "📱 Latest electronic gadgets and devices"),
            ("Clothing & Fashion", "clothing-fashion", "👕 Trendy clothes and accessories"),
            ("Food & Beverages", "food-beverages", "🍕 Fresh food and drinks"),
            ("Home & Kitchen", "home-kitchen", "🏠 Home essentials and appliances"),
            ("Books & Stationery", "books-stationery", "📚 Books and office supplies"),
            ("Sports & Fitness", "sports-fitness", "⚽ Sports equipment and fitness gear"),
            ("Beauty & Personal Care", "beauty-care", "💄 Cosmetics and personal care"),
            ("Toys & Games", "toys-games", "🎮 Fun toys and gaming"),
        ]

        for name, slug, desc in root_categories:
            category = Category(
                name=name,
                slug=slug,
                description=desc,
                is_active=True,
                is_featured=random.choice([True, False]),
                display_order=len(self.categories)
            )
            db.add(category)
            await db.flush()
            self.categories.append(category)

        # Subcategories for Electronics
        electronics = self.categories[0]
        electronics_subs = [
            ("Smartphones", "Latest smartphones and accessories"),
            ("Laptops & Computers", "Laptops, desktops, and peripherals"),
            ("Televisions", "Smart TVs and home entertainment"),
            ("Audio Devices", "Headphones, speakers, and audio systems"),
            ("Cameras", "Digital cameras and photography equipment"),
        ]

        for name, desc in electronics_subs:
            category = Category(
                name=name,
                slug=slugify(name),
                description=desc,
                parent_id=electronics.id,
                is_active=True,
            )
            db.add(category)
            await db.flush()
            self.categories.append(category)

        # Subcategories for Clothing
        clothing = self.categories[1]
        clothing_subs = [
            ("Men's Clothing", "Men's fashion and accessories"),
            ("Women's Clothing", "Women's fashion and accessories"),
            ("Kids' Clothing", "Children's clothing and accessories"),
            ("Footwear", "Shoes and sandals for all"),
        ]

        for name, desc in clothing_subs:
            category = Category(
                name=name,
                slug=slugify(name),
                description=desc,
                parent_id=clothing.id,
                is_active=True,
            )
            db.add(category)
            await db.flush()
            self.categories.append(category)

        await db.commit()

    async def generate_users(self, db: AsyncSession):
        """Generate users with different roles."""
        # Generate customers
        for i in range(50):
            email = f"customer{i+1}@example.com"
            user = User(
                email=email,
                phone=f"+91{fake.msisdn()[3:]}",
                password_hash=hash_password("Test@1234"),
                role=UserRole.CUSTOMER,
                is_active=True,
                is_verified=random.choice([True, False]),
                email_verified=random.choice([True, False]),
                phone_verified=random.choice([True, False]),
                profile_completion=random.uniform(0.3, 1.0),
            )
            db.add(user)
            await db.flush()

            # Create profile
            profile = UserProfile(
                user_id=user.id,
                full_name=fake.name(),
                date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=70),
                gender=random.choice(['male', 'female', 'other']),
                address_line1=fake.street_address(),
                city=fake.city(),
                state=random.choice(['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Gujarat']),
                country="India",
                pincode=fake.postcode(),
                latitude=float(fake.latitude()),
                longitude=float(fake.longitude()),
            )
            db.add(profile)
            self.users.append(user)
            self.customers.append(user)

        # Generate retailers
        for i in range(20):
            email = f"retailer{i+1}@example.com"
            user = User(
                email=email,
                phone=f"+91{fake.msisdn()[3:]}",
                password_hash=hash_password("Test@1234"),
                role=UserRole.RETAILER,
                is_active=True,
                is_verified=True,
                email_verified=True,
                phone_verified=True,
                profile_completion=0.9,
            )
            db.add(user)
            await db.flush()

            # Create profile with business info
            profile = UserProfile(
                user_id=user.id,
                full_name=fake.name(),
                city=fake.city(),
                state=random.choice(['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Gujarat']),
                country="India",
                pincode=fake.postcode(),
                business_name=f"{fake.company()} Store",
                business_type=random.choice(['Electronics', 'Clothing', 'Grocery', 'General']),
                gst_number=f"27{fake.bothify(text='?????')}0000A1Z5".upper(),
                business_description=fake.catch_phrase(),
            )
            db.add(profile)
            self.users.append(user)
            self.retailers.append(user)

        # Generate wholesalers
        for i in range(10):
            email = f"wholesaler{i+1}@example.com"
            user = User(
                email=email,
                phone=f"+91{fake.msisdn()[3:]}",
                password_hash=hash_password("Test@1234"),
                role=UserRole.WHOLESALER,
                is_active=True,
                is_verified=True,
                email_verified=True,
                phone_verified=True,
                profile_completion=1.0,
            )
            db.add(user)
            await db.flush()

            # Create profile with business info
            profile = UserProfile(
                user_id=user.id,
                full_name=fake.name(),
                city=fake.city(),
                state=random.choice(['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Gujarat']),
                country="India",
                pincode=fake.postcode(),
                business_name=f"{fake.company()} Wholesale",
                business_type=random.choice(['Electronics', 'FMCG', 'Textiles', 'General']),
                gst_number=f"27{fake.bothify(text='?????')}0000A1Z5".upper(),
                business_description=fake.bs(),
            )
            db.add(profile)
            self.users.append(user)
            self.wholesalers.append(user)

        await db.commit()

    async def generate_products(self, db: AsyncSession):
        """Generate products across categories."""
        # Product templates by category
        product_templates = {
            "Smartphones": [
                ("Apple iPhone 14 Pro", 89999, "Latest iPhone with A16 Bionic chip", "Apple"),
                ("Samsung Galaxy S23", 74999, "Flagship Samsung with excellent camera", "Samsung"),
                ("OnePlus 11", 56999, "Powerful performance with OxygenOS", "OnePlus"),
                ("Xiaomi 13 Pro", 64999, "Premium Xiaomi flagship", "Xiaomi"),
                ("Google Pixel 7", 59999, "Pure Android experience", "Google"),
            ],
            "Laptops & Computers": [
                ("MacBook Air M2", 114900, "Thin, light, powerful laptop", "Apple"),
                ("Dell XPS 13", 94990, "Premium Windows laptop", "Dell"),
                ("HP Pavilion 15", 55990, "Versatile everyday laptop", "HP"),
                ("Lenovo ThinkPad", 75990, "Business-class laptop", "Lenovo"),
                ("Asus ROG Gaming", 124990, "High-performance gaming laptop", "Asus"),
            ],
            "Men's Clothing": [
                ("Cotton Casual Shirt", 999, "Comfortable casual shirt", "Arrow"),
                ("Formal Trousers", 1499, "Professional formal trousers", "Van Heusen"),
                ("Denim Jeans", 1799, "Classic blue denim jeans", "Levi's"),
                ("Sports T-Shirt", 599, "Breathable sports tee", "Nike"),
                ("Winter Jacket", 2999, "Warm winter jacket", "Columbia"),
            ],
            "Food & Beverages": [
                ("Organic Basmati Rice 5kg", 499, "Premium quality rice", "India Gate"),
                ("Fresh Milk 1L", 65, "Farm fresh milk", "Amul"),
                ("Whole Wheat Atta 10kg", 450, "Nutritious wheat flour", "Aashirvaad"),
                ("Green Tea 100 Bags", 299, "Healthy green tea", "Lipton"),
                ("Honey 500g", 399, "Pure natural honey", "Dabur"),
            ],
        }

        for category_name, products in product_templates.items():
            category = next((c for c in self.categories if c.name == category_name), None)
            if not category:
                continue

            for name, price, desc, brand in products:
                # Create multiple variants
                for _ in range(random.randint(1, 3)):
                    variant_name = name if _ == 0 else f"{name} - Variant {_+1}"
                    product = Product(
                        name=variant_name,
                        slug=slugify(variant_name) + f"-{fake.uuid4()[:8]}",
                        description=f"{desc}. {fake.text(max_nb_chars=200)}",
                        short_description=desc,
                        category_id=category.id,
                        base_price=price * random.uniform(0.9, 1.1),
                        mrp=price * 1.2,
                        discount_percentage=random.uniform(0, 25),
                        brand=brand,
                        manufacturer=brand,
                        unit_type=random.choice(['piece', 'kg', 'liter', 'box']),
                        unit_value=1.0,
                        images=[
                            f"https://picsum.photos/seed/{fake.uuid4()}/800/600",
                            f"https://picsum.photos/seed/{fake.uuid4()}/800/600",
                        ],
                        thumbnail_url=f"https://picsum.photos/seed/{fake.uuid4()}/400/300",
                        is_local_product=random.choice([True, False]),
                        region_tags=['India', random.choice(['Maharashtra', 'Delhi', 'Karnataka'])],
                        is_active=True,
                        is_featured=random.choice([True, False]),
                        specifications={
                            "warranty": f"{random.randint(6, 24)} months",
                            "color": random.choice(['Black', 'White', 'Blue', 'Red']),
                        },
                        meta_title=variant_name,
                        meta_description=desc,
                    )
                    db.add(product)
                    await db.flush()
                    self.products.append(product)

        await db.commit()

    async def generate_inventory(self, db: AsyncSession):
        """Generate inventory for products."""
        for product in self.products:
            # Retailers have inventory
            for retailer in random.sample(self.retailers, k=min(3, len(self.retailers))):
                inventory = Inventory(
                    product_id=product.id,
                    owner_id=retailer.id,
                    owner_type=OwnerType.RETAILER,
                    quantity_available=random.randint(10, 500),
                    reorder_level=random.randint(5, 20),
                    reorder_quantity=random.randint(20, 100),
                    price=product.base_price * random.uniform(0.95, 1.05),
                    discount_percentage=random.uniform(0, 15),
                    is_available=True,
                )
                db.add(inventory)

            # Wholesalers have inventory
            for wholesaler in random.sample(self.wholesalers, k=min(2, len(self.wholesalers))):
                inventory = Inventory(
                    product_id=product.id,
                    owner_id=wholesaler.id,
                    owner_type=OwnerType.WHOLESALER,
                    quantity_available=random.randint(100, 5000),
                    reorder_level=random.randint(50, 200),
                    reorder_quantity=random.randint(200, 1000),
                    price=product.base_price * random.uniform(0.85, 0.95),
                    discount_percentage=random.uniform(5, 20),
                    is_available=True,
                )
                db.add(inventory)

        await db.commit()

    async def generate_orders(self, db: AsyncSession):
        """Generate order history."""
        for customer in self.customers[:30]:  # First 30 customers make orders
            num_orders = random.randint(1, 5)

            for _ in range(num_orders):
                # Select 1-4 random products
                order_products = random.sample(self.products, k=random.randint(1, 4))

                # Calculate order totals
                subtotal = sum(p.base_price * random.randint(1, 3) for p in order_products)
                tax_amount = subtotal * 0.18
                delivery_charge = random.choice([0, 40, 60, 80])
                total = subtotal + tax_amount + delivery_charge

                # Create order
                order = Order(
                    order_number=generate_order_number(),
                    customer_id=customer.id,
                    order_type=OrderType.ONLINE,
                    subtotal_amount=subtotal,
                    tax_amount=tax_amount,
                    delivery_charge=delivery_charge,
                    total_amount=total,
                    payment_status=random.choice([PaymentStatus.COMPLETED, PaymentStatus.PENDING]),
                    payment_method=random.choice([PaymentMethod.ONLINE, PaymentMethod.COD]),
                    delivery_address={
                        "name": customer.profile.full_name if customer.profile else "Customer",
                        "phone": customer.phone,
                        "address": fake.address(),
                        "city": customer.profile.city if customer.profile else fake.city(),
                        "pincode": customer.profile.pincode if customer.profile else fake.postcode(),
                    },
                    order_status=random.choice([
                        OrderStatus.DELIVERED,
                        OrderStatus.SHIPPED,
                        OrderStatus.PROCESSING,
                    ]),
                    created_at=fake.date_time_between(start_date='-60d', end_date='now'),
                )
                db.add(order)
                await db.flush()

                # Create order items
                for product in order_products:
                    quantity = random.randint(1, 3)
                    unit_price = product.base_price
                    order_item = OrderItem(
                        order_id=order.id,
                        product_id=product.id,
                        product_name=product.name,
                        quantity=quantity,
                        unit_price=unit_price,
                        discount_percentage=product.discount_percentage,
                        total_price=unit_price * quantity,
                    )
                    db.add(order_item)

                # Create payment
                if order.payment_status == PaymentStatus.COMPLETED:
                    payment = Payment(
                        order_id=order.id,
                        payment_gateway='razorpay',
                        payment_gateway_id=f"pay_{fake.uuid4()[:20]}",
                        amount=total,
                        currency='INR',
                        status=PaymentStatus.COMPLETED,
                    )
                    db.add(payment)

        await db.commit()

    async def generate_reviews(self, db: AsyncSession):
        """Generate product reviews."""
        # Get completed orders
        result = await db.execute(
            "SELECT id, customer_id FROM orders WHERE order_status = 'delivered' LIMIT 50"
        )
        orders = result.fetchall() if hasattr(result, 'fetchall') else []

        for _ in range(100):
            customer = random.choice(self.customers)
            product = random.choice(self.products)

            review = Review(
                product_id=product.id,
                user_id=customer.id,
                rating=random.randint(3, 5),
                title=fake.sentence(nb_words=6),
                comment=fake.text(max_nb_chars=200),
                is_verified_purchase=random.choice([True, False]),
                helpful_count=random.randint(0, 50),
                is_approved=True,
            )
            db.add(review)

        await db.commit()

    async def generate_interactions(self, db: AsyncSession):
        """Generate user interaction data for ML."""
        interaction_types = [
            InteractionType.VIEW,
            InteractionType.ADD_TO_CART,
            InteractionType.PURCHASE,
        ]

        for customer in self.customers:
            # Each customer has 5-20 interactions
            for _ in range(random.randint(5, 20)):
                interaction = UserInteraction(
                    user_id=customer.id,
                    product_id=random.choice(self.products).id,
                    interaction_type=random.choice(interaction_types),
                    session_id=fake.uuid4(),
                    timestamp=fake.date_time_between(start_date='-30d', end_date='now'),
                )
                db.add(interaction)

        await db.commit()

    async def generate_search_queries(self, db: AsyncSession):
        """Generate search query data."""
        search_terms = [
            "smartphone", "laptop", "shirt", "jeans", "rice", "milk",
            "headphones", "tv", "shoes", "watch", "bag", "camera",
        ]

        for _ in range(200):
            query = SearchQuery(
                user_id=random.choice(self.customers).id if random.random() > 0.3 else None,
                query_text=random.choice(search_terms),
                results_count=random.randint(0, 50),
                session_id=fake.uuid4(),
                timestamp=fake.date_time_between(start_date='-30d', end_date='now'),
            )
            db.add(query)

        await db.commit()

    async def generate_notifications(self, db: AsyncSession):
        """Generate notifications."""
        for customer in self.customers[:20]:
            for _ in range(random.randint(1, 3)):
                notification = Notification(
                    user_id=customer.id,
                    type=random.choice([
                        NotificationType.ORDER_UPDATE,
                        NotificationType.PROMOTION,
                        NotificationType.GENERAL,
                    ]),
                    title=fake.sentence(nb_words=5),
                    message=fake.text(max_nb_chars=100),
                    is_read=random.choice([True, False]),
                )
                db.add(notification)

        await db.commit()


async def main():
    """Main function to generate all mock data."""
    async with AsyncSessionLocal() as db:
        generator = MockDataGenerator()
        await generator.generate_all(db)
        print("\n✅ Mock data generation complete!")
        print(f"   - Users: {len(generator.users)}")
        print(f"   - Categories: {len(generator.categories)}")
        print(f"   - Products: {len(generator.products)}")


if __name__ == "__main__":
    asyncio.run(main())
