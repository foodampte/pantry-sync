# pantry-sync

A lightweight REST API to track pantry inventory and generate shopping lists based on meal plans.

---

## Installation

```bash
pip install -r requirements.txt
python app.py
```

---

## Usage

Start the server and interact with the API using any HTTP client.

**Add an item to your pantry:**
```bash
curl -X POST http://localhost:5000/pantry \
  -H "Content-Type: application/json" \
  -d '{"item": "olive oil", "quantity": 2, "unit": "bottle"}'
```

**Generate a shopping list from a meal plan:**
```bash
curl -X POST http://localhost:5000/shopping-list \
  -H "Content-Type: application/json" \
  -d '{"meals": ["pasta carbonara", "chicken stir fry"]}'
```

**Example response:**
```json
{
  "shopping_list": [
    {"item": "eggs", "quantity": 4},
    {"item": "chicken breast", "quantity": 2, "unit": "lbs"}
  ]
}
```

---

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/pantry` | List all pantry items |
| `POST` | `/pantry` | Add or update an item |
| `DELETE` | `/pantry/<item>` | Remove an item |
| `POST` | `/shopping-list` | Generate a shopping list |

---

## Requirements

- Python 3.9+
- Flask
- SQLite (included with Python)

---

## License

This project is licensed under the [MIT License](LICENSE).