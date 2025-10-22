# String Analyzer API 🔤

A RESTful API service that analyzes strings and stores their computed properties.

## Features

- ✅ Analyze strings (length, palindrome status, word count, SHA-256 hash, etc.)
- ✅ Store analyzed strings in PostgreSQL
- ✅ Filter strings by various properties
- ✅ Natural language query support
- ✅ Automatic API documentation (Swagger UI)

## Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL (Neon Cloud)
- **Deployment:** Railway
- **ORM:** SQLAlchemy
- **Validation:** Pydantic

## API Endpoints

| Endpoint                                  | Method | Description                            |
| ----------------------------------------- | ------ | -------------------------------------- |
| `POST /strings`                           | POST   | Create and analyze a new string        |
| `GET /strings/{value}`                    | GET    | Retrieve a specific string             |
| `GET /strings`                            | GET    | List all strings with optional filters |
| `GET /strings/filter-by-natural-language` | GET    | Filter using natural language          |
| `DELETE /strings/{value}`                 | DELETE | Delete a string                        |

## Documentation

Once deployed, visit:

- **Swagger UI:** `https://your-app.up.railway.app/docs`
- **ReDoc:** `https://your-app.up.railway.app/redoc`

## Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL (or use Neon cloud database)

### Setup

1. Clone the repository:

```bash
git clone <your-repo-url>
cd string-analyzer-api
```

2. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create `.env` file:

```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

5. Initialize database:

```bash
python create_tables.py
```

6. Run the API:

```bash
uvicorn app.main:app --reload
```

7. Visit: `http://127.0.0.1:8000/docs`

## Testing

Run the test suite:

```bash
python test_analyzer.py
python test_database.py
python test_schemas.py
python test_crud.py
python test_nlp_parser.py
python test_api.py  # Requires API to be running
```

## Environment Variables

| Variable       | Description                  | Required               |
| -------------- | ---------------------------- | ---------------------- |
| `DATABASE_URL` | PostgreSQL connection string | Yes                    |
| `PORT`         | Port to run the server on    | No (Railway sets this) |

## Railway Deployment

1. Connect your GitHub repository to Railway
2. Railway will automatically detect the configuration
3. Add `DATABASE_URL` environment variable (use your Neon database URL)
4. Railway will build and deploy automatically

### Railway Deployment Troubleshooting

If you encounter deployment issues:

1. **Database Connection Error**: Ensure `DATABASE_URL` is set in Railway environment variables
2. **Build Failures**: Check that all dependencies in `requirements.txt` are compatible
3. **Startup Errors**: The app now includes better error messages and startup validation

**Common Railway Environment Variables:**

- `DATABASE_URL`: Your PostgreSQL connection string (automatically provided by Railway if you add a PostgreSQL service)
- `PORT`: Automatically set by Railway (don't override this)

**Railway PostgreSQL Setup:**

1. Add a PostgreSQL service to your Railway project
2. Railway will automatically provide `DATABASE_URL`
3. The app will automatically convert `postgres://` to `postgresql://` if needed

## Example Queries

### Create a string

```bash
curl -X POST "https://your-app.up.railway.app/strings" \
  -H "Content-Type: application/json" \
  -d '{"value": "hello world"}'
```

### Filter palindromes

```bash
curl "https://your-app.up.railway.app/strings?is_palindrome=true"
```

### Natural language query

```bash
curl "https://your-app.up.railway.app/strings/filter-by-natural-language?query=all%20single%20word%20palindromes"
```

## License

MIT

## Author

Built with ❤️ using FastAPI
