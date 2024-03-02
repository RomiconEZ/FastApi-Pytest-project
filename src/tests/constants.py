from src.utils.auth import get_password_hash

SELLER_1_EXAMPLE_PASSWORD = "password_1"

HASH_SELLER_1_EXAMPLE = {
    "first_name": "Seller_1",
    "last_name": "Seller_1",
    "email": "seller_1@seller.seller",
    "password": get_password_hash(SELLER_1_EXAMPLE_PASSWORD),
}
SELLER_1_EXAMPLE = {
    "first_name": "Seller_1",
    "last_name": "Seller_1",
    "email": "seller_1@seller.seller",
    "password": SELLER_1_EXAMPLE_PASSWORD,
}
SELLER_2_EXAMPLE_PASSWORD = "password_2"
HASH_SELLER_2_EXAMPLE = {
    "first_name": "Seller_2",
    "last_name": "Seller_2",
    "email": "seller_2@seller.seller",
    "password": get_password_hash(SELLER_2_EXAMPLE_PASSWORD),
}
SELLER_2_EXAMPLE = {
    "first_name": "Seller_2",
    "last_name": "Seller_2",
    "email": "seller_2@seller.seller",
    "password": SELLER_2_EXAMPLE_PASSWORD,
}

PREFIX = "/api/v1/"

NEW_SELLER_1_EXAMPLE = {
    "first_name": "Seller_1_new",
    "last_name": "Seller_1_new",
    "email": "seller_1_new@seller.seller",
}
