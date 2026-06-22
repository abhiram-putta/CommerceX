"""
Realistic product data with actual brand names for Indian e-commerce.
Organized by category with real products and pricing.
"""

# Indian E-commerce Product Database with Real Brands

PRODUCT_CATALOG = {
    "Smartphones": [
        # Apple
        ("Apple iPhone 15 Pro Max 256GB", 159900, "Latest iPhone with A17 Pro chip, titanium design", "Apple", "piece"),
        ("Apple iPhone 15 Pro 128GB", 134900, "Pro camera system with 48MP main camera", "Apple", "piece"),
        ("Apple iPhone 15 Plus 128GB", 89900, "6.7-inch Super Retina XDR display", "Apple", "piece"),
        ("Apple iPhone 15 128GB", 79900, "Dynamic Island, 48MP camera", "Apple", "piece"),
        ("Apple iPhone 14 128GB", 69900, "A15 Bionic chip, dual camera system", "Apple", "piece"),
        ("Apple iPhone 13 128GB", 59900, "5G capable, advanced dual-camera", "Apple", "piece"),
        ("Apple iPhone SE (2022) 64GB", 43900, "Affordable iPhone with A15 Bionic", "Apple", "piece"),

        # Samsung
        ("Samsung Galaxy S24 Ultra 256GB", 129999, "AI-powered smartphone with S Pen", "Samsung", "piece"),
        ("Samsung Galaxy S24 Plus 256GB", 99999, "Premium flagship with triple camera", "Samsung", "piece"),
        ("Samsung Galaxy S24 128GB", 79999, "Compact flagship performance", "Samsung", "piece"),
        ("Samsung Galaxy S23 FE 128GB", 59999, "Fan edition with flagship features", "Samsung", "piece"),
        ("Samsung Galaxy A54 5G 128GB", 38999, "Mid-range with great camera", "Samsung", "piece"),
        ("Samsung Galaxy A34 5G 128GB", 30999, "Affordable 5G smartphone", "Samsung", "piece"),
        ("Samsung Galaxy M34 5G 128GB", 18999, "Budget 5G with big battery", "Samsung", "piece"),
        ("Samsung Galaxy F54 5G 256GB", 29999, "Photography focused mid-ranger", "Samsung", "piece"),

        # OnePlus
        ("OnePlus 12 256GB", 64999, "Flagship killer with Snapdragon 8 Gen 3", "OnePlus", "piece"),
        ("OnePlus 11 5G 256GB", 56999, "Hasselblad camera, fast charging", "OnePlus", "piece"),
        ("OnePlus Nord 3 5G 128GB", 33999, "MediaTek Dimensity powered", "OnePlus", "piece"),
        ("OnePlus Nord CE 3 5G 128GB", 26999, "Affordable Nord experience", "OnePlus", "piece"),

        # Xiaomi
        ("Xiaomi 14 Pro 256GB", 79999, "Leica cameras, Snapdragon 8 Gen 3", "Xiaomi", "piece"),
        ("Xiaomi 13 Pro 256GB", 69999, "Professional photography phone", "Xiaomi", "piece"),
        ("Redmi Note 13 Pro Plus 5G 256GB", 31999, "200MP camera, curved display", "Redmi", "piece"),
        ("Redmi Note 13 Pro 5G 128GB", 23999, "Great value mid-ranger", "Redmi", "piece"),
        ("Redmi Note 13 5G 128GB", 17999, "Affordable 5G smartphone", "Redmi", "piece"),
        ("Poco X6 Pro 5G 256GB", 26999, "Gaming focused mid-ranger", "Poco", "piece"),
        ("Poco F5 5G 256GB", 29999, "Flagship killer performance", "Poco", "piece"),

        # Vivo
        ("Vivo X100 Pro 256GB", 89999, "Zeiss optics, flagship camera", "Vivo", "piece"),
        ("Vivo V30 Pro 256GB", 41999, "Selfie focused premium phone", "Vivo", "piece"),
        ("Vivo V29 5G 128GB", 32999, "Aura light portrait system", "Vivo", "piece"),
        ("Vivo T3 5G 128GB", 19999, "Performance oriented mid-ranger", "Vivo", "piece"),

        # Oppo
        ("Oppo Find X7 Ultra 256GB", 99999, "Hasselblad quad camera flagship", "Oppo", "piece"),
        ("Oppo Reno 11 Pro 5G 256GB", 39999, "Portrait expert smartphone", "Oppo", "piece"),
        ("Oppo Reno 11 5G 128GB", 32999, "Stylish mid-range phone", "Oppo", "piece"),
        ("Oppo A79 5G 128GB", 18999, "Affordable 5G option", "Oppo", "piece"),

        # Realme
        ("Realme GT 5 Pro 256GB", 42999, "Flagship performance phone", "Realme", "piece"),
        ("Realme 12 Pro Plus 5G 256GB", 29999, "Periscope telephoto camera", "Realme", "piece"),
        ("Realme 12 Pro 5G 128GB", 23999, "Premium mid-ranger", "Realme", "piece"),
        ("Realme Narzo 70 Pro 5G 128GB", 19999, "Gaming oriented phone", "Realme", "piece"),

        # Google
        ("Google Pixel 8 Pro 256GB", 106999, "AI-powered camera, pure Android", "Google", "piece"),
        ("Google Pixel 8 128GB", 75999, "Best Android camera experience", "Google", "piece"),
        ("Google Pixel 7a 128GB", 43999, "Affordable Pixel experience", "Google", "piece"),

        # Motorola
        ("Motorola Edge 50 Ultra 256GB", 59999, "Premium flagship phone", "Motorola", "piece"),
        ("Motorola Edge 40 Neo 256GB", 25999, "Compact flagship experience", "Motorola", "piece"),
        ("Moto G84 5G 256GB", 18999, "OLED display mid-ranger", "Motorola", "piece"),
    ],

    "Laptops & Computers": [
        # Apple MacBooks
        ("Apple MacBook Air M3 13-inch 256GB", 114900, "Ultra-portable laptop with M3 chip", "Apple", "piece"),
        ("Apple MacBook Air M2 13-inch 256GB", 99900, "Thin and light with M2 performance", "Apple", "piece"),
        ("Apple MacBook Air M1 13-inch 256GB", 74900, "Best value MacBook", "Apple", "piece"),
        ("Apple MacBook Pro 14-inch M3 Pro 512GB", 199900, "Professional laptop for creators", "Apple", "piece"),
        ("Apple MacBook Pro 16-inch M3 Max 1TB", 349900, "Ultimate creative workstation", "Apple", "piece"),

        # Dell
        ("Dell XPS 13 Plus 12th Gen i7 512GB", 159990, "Premium ultrabook with stunning display", "Dell", "piece"),
        ("Dell XPS 15 12th Gen i7 1TB RTX 3050", 189990, "Creator laptop with dedicated GPU", "Dell", "piece"),
        ("Dell Inspiron 15 3520 11th Gen i5 512GB", 54990, "Reliable everyday laptop", "Dell", "piece"),
        ("Dell G15 Gaming 12th Gen i7 RTX 4060", 109990, "Gaming laptop for enthusiasts", "Dell", "piece"),
        ("Dell Alienware m15 R7 12th Gen i9 RTX 4070", 219990, "Premium gaming machine", "Dell", "piece"),

        # HP
        ("HP Spectre x360 14 12th Gen i7 1TB", 169990, "Convertible premium laptop", "HP", "piece"),
        ("HP Envy 13 12th Gen i5 512GB", 89990, "Stylish ultrabook for professionals", "HP", "piece"),
        ("HP Pavilion 15 12th Gen i5 512GB", 65990, "All-purpose family laptop", "HP", "piece"),
        ("HP Pavilion Gaming 15 12th Gen i5 RTX 3050", 79990, "Budget gaming laptop", "HP", "piece"),
        ("HP Omen 16 12th Gen i7 RTX 4070", 149990, "High-performance gaming", "HP", "piece"),

        # Lenovo
        ("Lenovo ThinkPad X1 Carbon Gen 11 i7 1TB", 189990, "Business ultrabook premium", "Lenovo", "piece"),
        ("Lenovo ThinkPad E14 Gen 5 i5 512GB", 64990, "Affordable business laptop", "Lenovo", "piece"),
        ("Lenovo IdeaPad Slim 3 12th Gen i5 512GB", 52990, "Budget-friendly thin and light", "Lenovo", "piece"),
        ("Lenovo Legion 5 Pro Ryzen 7 RTX 4060", 129990, "Gaming powerhouse", "Lenovo", "piece"),
        ("Lenovo Yoga 9i 12th Gen i7 1TB", 159990, "Premium 2-in-1 convertible", "Lenovo", "piece"),

        # Asus
        ("Asus ZenBook 14 OLED 12th Gen i7 512GB", 99990, "OLED display ultrabook", "Asus", "piece"),
        ("Asus VivoBook 15 11th Gen i5 512GB", 54990, "Colorful everyday laptop", "Asus", "piece"),
        ("Asus ROG Strix G16 13th Gen i9 RTX 4070", 189990, "Gaming laptop flagship", "Asus", "piece"),
        ("Asus TUF Gaming A15 Ryzen 7 RTX 4050", 94990, "Durable gaming laptop", "Asus", "piece"),
        ("Asus ProArt StudioBook 16 OLED i9 RTX 4060", 229990, "Creator workstation", "Asus", "piece"),

        # Acer
        ("Acer Swift 3 OLED 12th Gen i5 512GB", 74990, "Lightweight productivity laptop", "Acer", "piece"),
        ("Acer Aspire 5 11th Gen i5 512GB", 49990, "Budget all-purpose laptop", "Acer", "piece"),
        ("Acer Nitro 5 12th Gen i5 RTX 4050", 84990, "Gaming laptop value champion", "Acer", "piece"),
        ("Acer Predator Helios 300 i7 RTX 4060", 139990, "Mid-range gaming beast", "Acer", "piece"),
    ],

    "Snacks & Chips": [
        # Lays
        ("Lays Classic Salted 52g", 20, "India's favorite potato chips", "Lays", "pack"),
        ("Lays Magic Masala 52g", 20, "Spicy Indian masala flavor", "Lays", "pack"),
        ("Lays American Style Cream & Onion 52g", 20, "Creamy onion flavored chips", "Lays", "pack"),
        ("Lays Spanish Tomato Tango 52g", 20, "Tangy tomato flavor", "Lays", "pack"),
        ("Lays Sizzling Hot 52g", 20, "Extra spicy chips", "Lays", "pack"),
        ("Lays India's Magic Masala Family Pack 145g", 50, "Larger pack for families", "Lays", "pack"),
        ("Lays Classic Salted Party Pack 300g", 99, "Party size pack", "Lays", "pack"),

        # Kurkure
        ("Kurkure Masala Munch 85g", 20, "Crunchy masala snack", "Kurkure", "pack"),
        ("Kurkure Solid Masti 82g", 20, "Chatpata tomato flavor", "Kurkure", "pack"),
        ("Kurkure Chilli Chatka 85g", 20, "Spicy chilli flavor", "Kurkure", "pack"),
        ("Kurkure Puffcorn Yummy Cheese 68g", 20, "Cheese flavored corn puffs", "Kurkure", "pack"),
        ("Kurkure Hyderabadi Hungama 90g", 20, "Hyderabad style spicy", "Kurkure", "pack"),

        # Bingo
        ("Bingo! Mad Angles Achari Masti 72g", 20, "Pickle flavored chips", "Bingo", "pack"),
        ("Bingo! Mad Angles Masala Madness 72g", 20, "Spicy masala triangles", "Bingo", "pack"),
        ("Bingo! Original Style Salted 70g", 20, "Classic salted chips", "Bingo", "pack"),
        ("Bingo! Tedhe Medhe Masala Tadka 52g", 10, "Twisted masala snack", "Bingo", "pack"),
        ("Bingo! Yumitos Party Pack 120g", 40, "Fiesta pack Mexican flavor", "Bingo", "pack"),

        # Doritos
        ("Doritos Nacho Cheese 44g", 20, "Cheesy tortilla chips", "Doritos", "pack"),
        ("Doritos Sweet Chilli 44g", 20, "Sweet and spicy flavor", "Doritos", "pack"),
        ("Doritos Mexicana 150g", 75, "Mexican spices party pack", "Doritos", "pack"),

        # Cheetos
        ("Cheetos Crunchy Flamin Hot 56.7g", 20, "Spicy cheese puffs", "Cheetos", "pack"),
        ("Cheetos Masala Balls 42g", 10, "Cheesy masala balls", "Cheetos", "pack"),

        # Uncle Chipps
        ("Uncle Chipps Spicy Treat 55g", 20, "Desi spicy potato chips", "Uncle Chipps", "pack"),
        ("Uncle Chipps Pepper Blast 55g", 20, "Black pepper flavor", "Uncle Chipps", "pack"),

        # Haldiram's
        ("Haldiram's Aloo Bhujia 200g", 50, "Classic Indian savory snack", "Haldiram's", "pack"),
        ("Haldiram's Moong Dal 200g", 55, "Fried split moong dal", "Haldiram's", "pack"),
        ("Haldiram's Khatta Meetha 200g", 55, "Sweet and salty mix", "Haldiram's", "pack"),
        ("Haldiram's Navrattan Mix 200g", 60, "Nine ingredient mix", "Haldiram's", "pack"),
        ("Haldiram's Punjabi Tadka 200g", 55, "Punjabi style mix", "Haldiram's", "pack"),
        ("Haldiram's Bhel Puri 150g", 45, "Ready to eat bhel", "Haldiram's", "pack"),

        # Bikano
        ("Bikano Aloo Bhujia 400g", 80, "Traditional namkeen", "Bikano", "pack"),
        ("Bikano Raita Boondi 400g", 85, "Boondi for raita", "Bikano", "pack"),
        ("Bikano Tasty Nuts 200g", 110, "Spiced peanuts", "Bikano", "pack"),

        # Balaji
        ("Balaji Wafers Masala Masti 135g", 40, "Mumbai's favorite chips", "Balaji", "pack"),
        ("Balaji Wafers Salted 135g", 40, "Classic potato wafers", "Balaji", "pack"),
        ("Balaji Wafers Tomato Twist 135g", 40, "Tangy tomato flavor", "Balaji", "pack"),

        # Pringles
        ("Pringles Original 107g", 99, "Stackable potato crisps", "Pringles", "pack"),
        ("Pringles Sour Cream & Onion 107g", 99, "Creamy flavor crisps", "Pringles", "pack"),
        ("Pringles Hot & Spicy 107g", 99, "Spicy stackable chips", "Pringles", "pack"),
    ],

    "Beverages": [
        # Coca-Cola
        ("Coca-Cola 750ml", 40, "Classic cola drink", "Coca-Cola", "bottle"),
        ("Coca-Cola 2.25L", 90, "Family size cola", "Coca-Cola", "bottle"),
        ("Coca-Cola 600ml", 35, "Personal size", "Coca-Cola", "bottle"),
        ("Coca-Cola Zero Sugar 750ml", 40, "Zero calorie cola", "Coca-Cola", "bottle"),

        # Pepsi
        ("Pepsi 750ml", 40, "Refreshing cola", "Pepsi", "bottle"),
        ("Pepsi 2.25L", 90, "Family pack", "Pepsi", "bottle"),
        ("Pepsi Black 600ml", 35, "Zero sugar cola", "Pepsi", "bottle"),

        # Sprite
        ("Sprite 750ml", 40, "Lemon-lime soda", "Sprite", "bottle"),
        ("Sprite 2L", 85, "Clear refreshment", "Sprite", "bottle"),

        # Fanta
        ("Fanta Orange 750ml", 40, "Orange flavored soda", "Fanta", "bottle"),
        ("Fanta Apple 600ml", 35, "Apple flavor drink", "Fanta", "bottle"),

        # Thums Up
        ("Thums Up 750ml", 40, "India's thunder cola", "Thums Up", "bottle"),
        ("Thums Up Charged 500ml", 30, "Extra caffeine cola", "Thums Up", "bottle"),

        # Mountain Dew
        ("Mountain Dew 750ml", 40, "Citrus blast drink", "Mountain Dew", "bottle"),
        ("Mountain Dew Ice 600ml", 35, "Cool citrus flavor", "Mountain Dew", "bottle"),

        # Limca
        ("Limca 750ml", 40, "Lemon fresh drink", "Limca", "bottle"),
        ("Limca Sportz 500ml", 30, "Sports drink variant", "Limca", "bottle"),

        # Maaza
        ("Maaza Mango 1.2L", 60, "Mango fruit drink", "Maaza", "bottle"),
        ("Maaza Guava 1L", 50, "Guava fruit drink", "Maaza", "bottle"),

        # Frooti
        ("Frooti Mango 1.2L", 55, "Fresh n juicy mango", "Frooti", "bottle"),
        ("Frooti Fizz 250ml", 20, "Fizzy mango drink", "Frooti", "bottle"),

        # Real Juice
        ("Real Fruit Power Mixed Fruit 1L", 110, "100% fruit juice", "Real", "bottle"),
        ("Real Activ Fiber Plus Apple 1L", 135, "Fiber enriched juice", "Real", "bottle"),
        ("Real Mango Juice 1L", 99, "Pure mango juice", "Real", "bottle"),
        ("Real Orange Juice 1L", 99, "Fresh orange juice", "Real", "bottle"),

        # Tropicana
        ("Tropicana 100% Orange Juice 1L", 130, "No added sugar juice", "Tropicana", "bottle"),
        ("Tropicana Mixed Fruit 1L", 125, "Mixed fruit delight", "Tropicana", "bottle"),
        ("Tropicana Pomegranate 200ml", 35, "Antioxidant rich juice", "Tropicana", "bottle"),

        # Paper Boat
        ("Paper Boat Aamras 250ml", 35, "Mango pulp drink", "Paper Boat", "bottle"),
        ("Paper Boat Jaljeera 250ml", 30, "Traditional Indian drink", "Paper Boat", "bottle"),
        ("Paper Boat Aam Panna 250ml", 30, "Raw mango cooler", "Paper Boat", "bottle"),

        # Red Bull
        ("Red Bull Energy Drink 250ml", 125, "Energy drink", "Red Bull", "can"),
        ("Red Bull Sugar Free 250ml", 125, "Zero sugar energy", "Red Bull", "can"),

        # Monster Energy
        ("Monster Energy Green 500ml", 125, "Energy drink classic", "Monster", "can"),
        ("Monster Energy Ultra 500ml", 130, "Zero sugar energy", "Monster", "can"),

        # Bisleri
        ("Bisleri Mineral Water 1L", 20, "Pure drinking water", "Bisleri", "bottle"),
        ("Bisleri 5L", 60, "Family pack water", "Bisleri", "bottle"),
        ("Bisleri Soda 750ml", 20, "Sparkling water", "Bisleri", "bottle"),

        # Aquafina
        ("Aquafina Drinking Water 1L", 20, "Purified water", "Aquafina", "bottle"),
        ("Aquafina Splash Lime 600ml", 30, "Flavored water", "Aquafina", "bottle"),

        # Kinley
        ("Kinley Water 1L", 20, "Safe drinking water", "Kinley", "bottle"),
        ("Kinley Club Soda 750ml", 20, "Carbonated water", "Kinley", "bottle"),
    ],

    "Dairy Products": [
        # Amul
        ("Amul Taaza Toned Milk 1L", 62, "Fresh toned milk", "Amul", "liter"),
        ("Amul Gold Full Cream Milk 1L", 72, "Rich full cream milk", "Amul", "liter"),
        ("Amul Slim & Trim Milk 1L", 68, "Low fat milk", "Amul", "liter"),
        ("Amul Masti Dahi 400g", 30, "Fresh curd", "Amul", "cup"),
        ("Amul Fresh Paneer 200g", 90, "Fresh cottage cheese", "Amul", "pack"),
        ("Amul Butter 100g", 56, "Utterly butterly delicious", "Amul", "pack"),
        ("Amul Butter 500g", 270, "Family pack butter", "Amul", "pack"),
        ("Amul Cheese Slices 200g", 135, "Processed cheese slices", "Amul", "pack"),
        ("Amul Cheese Cubes 200g", 110, "Cooking cheese cubes", "Amul", "pack"),
        ("Amul Kool Koko 200ml", 20, "Chocolate flavored milk", "Amul", "bottle"),
        ("Amul Kool Cafe 200ml", 25, "Coffee flavored milk", "Amul", "bottle"),
        ("Amul Lassi Sweet 200ml", 20, "Sweet lassi drink", "Amul", "bottle"),

        # Mother Dairy
        ("Mother Dairy Full Cream Milk 1L", 70, "Fresh full cream milk", "Mother Dairy", "liter"),
        ("Mother Dairy Token Milk 500ml", 30, "Fresh token milk", "Mother Dairy", "pack"),
        ("Mother Dairy Curd 400g", 28, "Fresh dahi", "Mother Dairy", "cup"),
        ("Mother Dairy Paneer 200g", 85, "Fresh paneer", "Mother Dairy", "pack"),
        ("Mother Dairy Ghee 1L", 650, "Pure cow ghee", "Mother Dairy", "bottle"),

        # Nestle
        ("Nestle Milkmaid Condensed Milk 380g", 170, "Sweetened condensed milk", "Nestle", "tin"),
        ("Nestle Everyday Dairy Whitener 400g", 185, "Tea whitener", "Nestle", "pack"),
        ("Nestle a+ Slim Milk 1L", 65, "Low fat milk", "Nestle", "liter"),

        # Britannia
        ("Britannia Cheese Slices 200g", 130, "Processed cheese", "Britannia", "pack"),
        ("Britannia Cheese Spread 180g", 115, "Creamy cheese spread", "Britannia", "jar"),
        ("Britannia Paneer 200g", 88, "Fresh paneer", "Britannia", "pack"),
    ],

    "Clothing - Men": [
        # Shirts
        ("Allen Solly Cotton Casual Shirt", 1599, "Premium cotton casual shirt", "Allen Solly", "piece"),
        ("Peter England Formal Shirt White", 1299, "Classic formal shirt", "Peter England", "piece"),
        ("Van Heusen Slim Fit Formal Shirt", 1799, "Premium formal shirt", "Van Heusen", "piece"),
        ("Raymond Linen Casual Shirt", 2199, "Breathable linen shirt", "Raymond", "piece"),
        ("Louis Philippe Formal Shirt", 1899, "Luxury formal shirt", "Louis Philippe", "piece"),
        ("Arrow Casual Shirt Blue", 1699, "Smart casual shirt", "Arrow", "piece"),
        ("US Polo Assn Casual Shirt", 1499, "Sporty casual shirt", "US Polo", "piece"),

        # T-Shirts
        ("Nike Dri-FIT Training T-Shirt", 1495, "Moisture wicking tee", "Nike", "piece"),
        ("Adidas Essential T-Shirt Black", 999, "Classic sports tee", "Adidas", "piece"),
        ("Puma Logo T-Shirt", 899, "Casual puma tee", "Puma", "piece"),
        ("H&M Cotton T-Shirt Pack of 3", 1499, "Value pack tees", "H&M", "pack"),
        ("Zara Basic T-Shirt", 1290, "Premium casual tee", "Zara", "piece"),
        ("Uniqlo AIRism T-Shirt", 990, "Ultra comfortable tee", "Uniqlo", "piece"),

        # Jeans
        ("Levi's 511 Slim Fit Jeans", 3199, "Iconic slim fit jeans", "Levi's", "piece"),
        ("Wrangler Regular Fit Jeans", 2299, "Classic denim jeans", "Wrangler", "piece"),
        ("Lee Cooper Skinny Jeans", 1999, "Modern skinny fit", "Lee Cooper", "piece"),
        ("Flying Machine Slim Jeans", 1799, "Trendy slim jeans", "Flying Machine", "piece"),
        ("Pepe Jeans Regular Fit", 2499, "Premium denim", "Pepe Jeans", "piece"),
        ("Jack & Jones Slim Fit Jeans", 2399, "European style jeans", "Jack & Jones", "piece"),

        # Trousers
        ("Allen Solly Formal Trousers", 1899, "Office wear trousers", "Allen Solly", "piece"),
        ("Van Heusen Chinos", 1999, "Casual chino trousers", "Van Heusen", "piece"),
        ("Arrow Formal Pants Black", 1799, "Premium formal pants", "Arrow", "piece"),
        ("Blackberrys Formal Trousers", 2199, "Luxury formal pants", "Blackberrys", "piece"),

        # Shoes
        ("Nike Air Max Running Shoes", 8995, "Cushioned running shoes", "Nike", "pair"),
        ("Adidas Ultraboost 23", 16999, "Premium running shoes", "Adidas", "pair"),
        ("Puma RS-X Sneakers", 6999, "Lifestyle sneakers", "Puma", "pair"),
        ("Woodland Leather Shoes", 3495, "Formal leather shoes", "Woodland", "pair"),
        ("Red Tape Casual Shoes", 2799, "Trendy casual shoes", "Red Tape", "pair"),
        ("Bata Formal Shoes", 1999, "Classic office shoes", "Bata", "pair"),

        # Ethnic Wear
        ("Manyavar Kurta Pajama Set", 2999, "Traditional kurta set", "Manyavar", "set"),
        ("Fabindia Cotton Kurta", 1590, "Handloom kurta", "Fabindia", "piece"),
    ],

    "Clothing - Women": [
        # Ethnic Wear
        ("Biba Anarkali Kurta Set", 2499, "Designer anarkali", "Biba", "set"),
        ("W for Woman Straight Kurta", 1599, "Contemporary kurta", "W for Woman", "piece"),
        ("Aurelia Printed Kurta", 1399, "Trendy printed kurta", "Aurelia", "piece"),
        ("Global Desi Palazzo Set", 1899, "Fusion ethnic wear", "Global Desi", "set"),
        ("FabIndia Cotton Kurta", 1490, "Handcrafted kurta", "Fabindia", "piece"),

        # Western Wear
        ("Zara Midi Dress", 2990, "Elegant midi dress", "Zara", "piece"),
        ("H&M Casual Dress", 1999, "Everyday casual dress", "H&M", "piece"),
        ("Forever 21 Top", 799, "Trendy crop top", "Forever 21", "piece"),
        ("Vero Moda Jeans", 1999, "Skinny fit jeans", "Vero Moda", "piece"),
        ("Only Top", 1299, "Casual western top", "Only", "piece"),

        # Sarees
        ("Soch Silk Saree", 3499, "Designer silk saree", "Soch", "piece"),
        ("FabIndia Cotton Saree", 2290, "Handloom saree", "Fabindia", "piece"),
    ],
}

# Helper function to get all products as a flat list
def get_all_products():
    """Returns all products as a flat list of tuples."""
    all_products = []
    for category, products in PRODUCT_CATALOG.items():
        for product in products:
            all_products.append((category, *product))
    return all_products
