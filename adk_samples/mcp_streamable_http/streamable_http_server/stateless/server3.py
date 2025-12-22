# server3.py
# -------------------------------------------------------------------------------------
# PURPOSE:
# This script launches a simple stateless MCP (Model Context Protocol) server using
# FastMCP, a high-level server abstraction from the MCP Python SDK.
#
# The server exposes tools for querying a books database to answer data analysis questions.
# The tools allow filtering books by genre, rating, year, and calculating averages.
#
# The tools are structured: both their input and output are defined using
# Pydantic models. This enables automatic schema validation and structured responses.
#
# The server uses the `streamable-http` transport, which allows communication
# over a modern HTTP streaming protocol that supports structured JSON-RPC calls.
#
# It is stateless, meaning it holds no memory or session information between calls.
# -------------------------------------------------------------------------------------

# === Imports ===

# click: For building command-line interfaces (CLI), such as --port and --log-level
import click

# logging: Standard Python module for displaying log messages to stdout/stderr
import logging

# sys: For exiting the program in case of errors (e.g., sys.exit(1))
import sys

# BaseModel and Field: From pydantic, used for structured input/output validation
from pydantic import BaseModel, Field
from typing import List, Dict, Any

# FastMCP: High-level abstraction that makes it easy to create and run MCP servers
from mcp.server.fastmcp import FastMCP

# === Data ===

BOOKS_DATABASE = [
    {
        "id": 1,
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "genre": "Classic Fiction",
        "year": 1925,
        "isbn": "978-0743273565",
        "available": True,
        "rating": 4.5,
    },
    {
        "id": 2,
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "genre": "Classic Fiction",
        "year": 1960,
        "isbn": "978-0446310789",
        "available": True,
        "rating": 4.8,
    },
    {
        "id": 3,
        "title": "1984",
        "author": "George Orwell",
        "genre": "Dystopian Fiction",
        "year": 1949,
        "isbn": "978-0451524935",
        "available": False,
        "rating": 4.7,
    },
    {
        "id": 4,
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "genre": "Romance",
        "year": 1813,
        "isbn": "978-0141439518",
        "available": True,
        "rating": 4.6,
    },
    {
        "id": 5,
        "title": "The Catcher in the Rye",
        "author": "J.D. Salinger",
        "genre": "Classic Fiction",
        "year": 1951,
        "isbn": "978-0316769488",
        "available": True,
        "rating": 4.2,
    },
    {
        "id": 6,
        "title": "Brave New World",
        "author": "Aldous Huxley",
        "genre": "Dystopian Fiction",
        "year": 1932,
        "isbn": "978-0060850524",
        "available": True,
        "rating": 4.4,
    },
    {
        "id": 7,
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "genre": "Fantasy",
        "year": 1937,
        "isbn": "978-0547928227",
        "available": False,
        "rating": 4.9,
    },
    {
        "id": 8,
        "title": "Fahrenheit 451",
        "author": "Ray Bradbury",
        "genre": "Dystopian Fiction",
        "year": 1953,
        "isbn": "978-1451673319",
        "available": True,
        "rating": 4.3,
    },
    {
        "id": 9,
        "title": "Dune",
        "author": "Frank Herbert",
        "genre": "Science Fiction",
        "year": 1965,
        "isbn": "978-0441172719",
        "available": True,
        "rating": 4.7,
    },
    {
        "id": 10,
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "genre": "Fantasy",
        "year": 1954,
        "isbn": "978-0544003415",
        "available": True,
        "rating": 4.9,
    },
]


@click.command()  # Defines a CLI command
@click.option("--port", default=3002, help="Port number to run the server on")
@click.option("--log-level", default="DEBUG", help="Logging level (e.g., DEBUG, INFO)")
def main(port: int, log_level: str) -> None:
    # === Logging Configuration ===
    # Sets the logging format and level based on the provided CLI argument
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.DEBUG),  # convert string to log level constant
        format="%(asctime)s - %(levelname)s - %(message)s",       # format: timestamp - level - message
    )
    logger = logging.getLogger(__name__)  # Logger instance scoped to this file/module
    logger.info("🚀 Starting Stateless Book Data Analyst MCP Server...")

    # === Create FastMCP Server ===
    # This initializes an MCP server with the following properties:
    # - Name: Appears in client UIs like Claude Desktop
    # - host: IP interface to bind (localhost means only local access)
    # - port: Port to serve on
    # - stateless_http=True: Ensures no session memory is kept between requests
    mcp = FastMCP(
        "Stateless Book Data Analyst Server",   # Server name
        host="localhost",          # Bind to localhost only
        port=port,                 # Use port from CLI flag
        stateless_http=True,      # Enforces stateless behavior
    )

    # === Define Models ===

    class Book(BaseModel):
        id: int = Field(..., description="Unique book ID")
        title: str = Field(..., description="Book title")
        author: str = Field(..., description="Book author")
        genre: str = Field(..., description="Book genre")
        year: int = Field(..., description="Publication year")
        isbn: str = Field(..., description="ISBN number")
        available: bool = Field(..., description="Availability status")
        rating: float = Field(..., description="Book rating")

    # --- THIS IS THE NEW, IMPORTANT MODEL FOR THE RETURN TYPE HINT ---
    class BooksList(BaseModel):
        books: List[Dict[str, Any]] = Field(..., description="A list of book objects.")

    # # class BooksList(BaseModel):
    # #     books: list[Book] = Field(..., description="List of books matching the query")

    class GenreInput(BaseModel):
        genre: str = Field(..., description="Genre to filter books by")

    # class GenreOutput(BaseModel):
    #     genre_out: str = Field(..., description="Popular Genre selected")

    class RatingInput(BaseModel):
        rating: float = Field(..., description="Minimum rating to filter books by")

    class YearInput(BaseModel):
        year: int = Field(..., description="Year to filter books by")

    class AverageRatingResult(BaseModel):
        average_rating: float = Field(..., description="Average rating of books in the genre")
        genre: str = Field(..., description="The genre queried")


    # === Register Tool: Get Average Rating by Genre ===
    @mcp.tool(description="Get the average rating of books in a specific genre", title="Get Average Rating by Genre")
    def get_average_rating_by_genre(params: GenreInput) -> AverageRatingResult:
        books = [b for b in BOOKS_DATABASE if b['genre'] == params.genre]
        if not books:
            return AverageRatingResult(average_rating=0.0, genre=params.genre)
        avg = sum(b['rating'] for b in books) / len(books)
        return AverageRatingResult(average_rating=avg, genre=params.genre)
    
    # === Register Tool: Get Books by Genre ===
    @mcp.tool(description="Get all books from a specific genre", title="Get Books by Genre")
    def get_books_by_genre(params: GenreInput) -> BooksList:
        books = [b for b in BOOKS_DATABASE if b['genre'] == params.genre]
        # return BooksList(books=[Book(**b) for b in books])
        
        # CHANGE #2: Return a simple dictionary, not a Pydantic model.
        # The structure should match what the agent expects.
        # No need to validate with Book(**b) here, as that's what creates the complex schema.
        return BooksList(books=books)

    # === Register Tool: Get Books by Rating Above ===
    @mcp.tool(description="Get all books with rating above a specified value", title="Get Books by Rating Above")
    def get_books_by_rating_above(params: RatingInput) -> BooksList:
        books = [b for b in BOOKS_DATABASE if b['rating'] > params.rating]
        return BooksList(books=books)
        # return BooksList(books=[Book(**b) for b in books])

    # === Register Tool: Get Books by Year ===
    @mcp.tool(description="Get all books released in a specific year", title="Get Books by Year")
    def get_books_by_year(params: YearInput) -> BooksList:
        books = [b for b in BOOKS_DATABASE if b['year'] == params.year]
        return BooksList(books=books)

    # === Run the Server ===
    try:
        # This starts the FastMCP server with streamable HTTP transport
        # It listens on /mcp endpoint and responds to JSON-RPC requests
        mcp.run(transport="streamable-http")
    except KeyboardInterrupt:
        # Handle Ctrl+C clean shutdown
        print("\n🛑 Server shutting down gracefully...")
    except Exception as e:
        # Handle any unhandled errors
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        # Final message on exit
        print("✅ Server exited.")

# === CLI Entry Point ===
# This block ensures the main() function only runs if the script is executed directly
if __name__ == "__main__":
    main()
