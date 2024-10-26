import random
import json
import spacy
from spacy.tokens import DocBin
from spacy.training import Example
from faker import Faker
import os

# Initialize Faker
fake = Faker()

# Product categories with carbon footprint data
products_data = {
    "Laptop": {"category": "Electronics", "base_footprint": 300},
    "Smartphone": {"category": "Electronics", "base_footprint": 100},
    "Headphones": {"category": "Electronics", "base_footprint": 30},
    "Smartwatch": {"category": "Electronics", "base_footprint": 50},
    "Tablet": {"category": "Electronics", "base_footprint": 150},
    "Camera": {"category": "Electronics", "base_footprint": 80},
    "Coffee Maker": {"category": "Appliances", "base_footprint": 120},
    "Air Purifier": {"category": "Appliances", "base_footprint": 200},
    "Electric Kettle": {"category": "Appliances", "base_footprint": 60},
    "Vacuum Cleaner": {"category": "Appliances", "base_footprint": 180}
}

def generate_sales_emails(num_emails=1000):
    emails = []
    for _ in range(num_emails):
        product = random.choice(list(products_data.keys()))
        customer_name = fake.name()
        order_id = fake.unique.uuid4()
        amount = f"${random.uniform(20, 2000):.2f}"
        date = fake.date_this_year().strftime("%Y-%m-%d")

        email_content = (
            f"Hello {customer_name},\n\n"
            f"Thank you for purchasing the {product}. Your order ID is {order_id}. "
            f"The total amount of {amount} was successfully processed on {date}. "
            "We'll notify you once your item ships.\n\n"
            "Best Regards,\nSales Team"
        )

        emails.append({
            "customer_name": customer_name,
            "product": product,
            "order_id": order_id,
            "amount": amount,
            "date": date,
            "email_content": email_content,
            "category": products_data[product]["category"],
            "carbon_footprint": products_data[product]["base_footprint"]
        })
    return emails

def train_model(output_dir):
    # Generate synthetic data
    emails = generate_sales_emails()
    
    # Save the generated emails
    with open(os.path.join(output_dir, "synthetic_sales_emails.json"), "w") as f:
        json.dump(emails, f, indent=4)
    
    # Save product carbon footprint data
    product_df = pd.DataFrame([
        {"product": k, "category": v["category"], "base_footprint": v["base_footprint"]}
        for k, v in products_data.items()
    ])
    product_df.to_csv(os.path.join(output_dir, "product_carbon_footprint.csv"), index=False)
    
    # Initialize spaCy model
    nlp = spacy.blank("en")
    
    # Extract entities from emails
    train_data = []
    for email in emails:
        text = email["email_content"]
        entities = []
        
        # Extract product
        if "product" in email:
            start = text.find(email["product"])
            if start != -1:
                entities.append((start, start + len(email["product"]), "Product_Name"))
        
        # Extract amount
        if "amount" in email:
            start = text.find(email["amount"])
            if start != -1:
                entities.append((start, start + len(email["amount"]), "Amount"))
        
        # Extract date
        if "date" in email:
            start = text.find(email["date"])
            if start != -1:
                entities.append((start, start + len(email["date"]), "Date"))
        
        # Extract order ID
        if "order_id" in email:
            start = text.find(email["order_id"])
            if start != -1:
                entities.append((start, start + len(email["order_id"]), "Order_ID"))
        
        train_data.append((text, {"entities": entities}))
    
    # Set up NER pipeline
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
    
    # Add labels
    for _, annotations in train_data:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])
    
    # Train the model
    n_iter = 20
    nlp.initialize()
    
    for itn in range(n_iter):
        random.shuffle(train_data)
        losses = {}
        for text, annotations in train_data:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            nlp.update([example], losses=losses)
        print(f"Iteration {itn + 1} - Loss: {losses}")
    
    # Save the model
    nlp.to_disk(os.path.join(output_dir, "email_parser_model"))
    
    return nlp

if __name__ == "__main__":
    output_dir = "models"
    os.makedirs(output_dir, exist_ok=True)
    trained_model = train_model(output_dir)
