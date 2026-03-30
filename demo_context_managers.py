"""
Demo script to showcase the context manager implementation.

This script demonstrates how the context managers handle various scenarios:
1. Normal file operations
2. Error recovery
3. Atomic writes
4. Missing file handling
"""

import os
import sys
import json
import tempfile
from storage import safe_file_write, safe_file_read

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    try:
        # Try to set UTF-8 encoding for Windows console
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass  # If it fails, emojis will be replaced


def demo_safe_file_write():
    """Demonstrate safe_file_write context manager."""
    print("=" * 60)
    print("DEMO 1: safe_file_write() - Normal Operation")
    print("=" * 60)
    
    # Create a temp file for demo
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        demo_file = tmp.name
    
    try:
        # Write data safely
        print(f"\n1. Writing to: {demo_file}")
        with safe_file_write(demo_file) as f:
            json.dump({"message": "Hello, Context Managers!"}, f, indent=2)
        print("   ✅ Write successful")
        
        # Verify content
        print("\n2. Reading back content:")
        with open(demo_file, 'r') as f:
            data = json.load(f)
            print(f"   📄 Content: {data}")
        
        print("\n✅ Demo 1 completed successfully\n")
    finally:
        # Cleanup
        if os.path.exists(demo_file):
            os.unlink(demo_file)


def demo_safe_file_write_error_recovery():
    """Demonstrate safe_file_write error recovery."""
    print("=" * 60)
    print("DEMO 2: safe_file_write() - Error Recovery")
    print("=" * 60)
    
    # Create a temp file for demo
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        demo_file = tmp.name
    
    try:
        # Write initial content
        print(f"\n1. Creating file with initial content: {demo_file}")
        with safe_file_write(demo_file) as f:
            json.dump({"version": 1, "data": "original"}, f, indent=2)
        print("   ✅ Initial write successful")
        
        # Read initial content
        with open(demo_file, 'r') as f:
            original_data = json.load(f)
            print(f"   📄 Original content: {original_data}")
        
        # Try to write invalid data (will fail)
        print("\n2. Attempting to write invalid data...")
        try:
            with safe_file_write(demo_file) as f:
                f.write("This is not valid JSON")
                f.write("{incomplete json")
                # Simulate an error
                raise ValueError("Simulated write error!")
        except ValueError as e:
            print(f"   ❌ Write failed (expected): {e}")
        
        # Verify original content is intact
        print("\n3. Verifying original file is unchanged:")
        with open(demo_file, 'r') as f:
            current_data = json.load(f)
            print(f"   📄 Current content: {current_data}")
            if current_data == original_data:
                print("   ✅ Original data intact (atomic write worked!)")
            else:
                print("   ❌ Data corrupted (shouldn't happen)")
        
        print("\n✅ Demo 2 completed - Error recovery verified\n")
    finally:
        # Cleanup
        if os.path.exists(demo_file):
            os.unlink(demo_file)


def demo_safe_file_read():
    """Demonstrate safe_file_read context manager."""
    print("=" * 60)
    print("DEMO 3: safe_file_read() - Missing File Handling")
    print("=" * 60)
    
    # Use a non-existent file
    nonexistent_file = "this_file_does_not_exist_12345.json"
    
    print(f"\n1. Attempting to read non-existent file: {nonexistent_file}")
    with safe_file_read(nonexistent_file) as f:
        if f is None:
            print("   ℹ️  File not found (no exception raised)")
            print("   ✅ Gracefully handled missing file")
        else:
            print("   ❌ Unexpected: File handle returned")
    
    # Now create the file and read it
    print("\n2. Creating file and reading it:")
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        demo_file = tmp.name
        json.dump({"status": "exists"}, tmp)
    
    try:
        print(f"   Reading: {demo_file}")
        with safe_file_read(demo_file) as f:
            if f is None:
                print("   ❌ File not found (shouldn't happen)")
            else:
                data = json.load(f)
                print(f"   📄 Content: {data}")
                print("   ✅ Successfully read existing file")
        
        print("\n✅ Demo 3 completed - Missing file handling verified\n")
    finally:
        # Cleanup
        if os.path.exists(demo_file):
            os.unlink(demo_file)


def demo_real_world_usage():
    """Demonstrate real-world usage with book data."""
    print("=" * 60)
    print("DEMO 4: Real-World Usage - Book Collection")
    print("=" * 60)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        demo_file = tmp.name
    
    try:
        # Simulate book collection operations
        books = [
            {
                "title": "The Pragmatic Programmer",
                "author": "Andy Hunt",
                "year": 1999,
                "read": True,
                "reviews": []
            },
            {
                "title": "Clean Code",
                "author": "Robert Martin",
                "year": 2008,
                "read": True,
                "reviews": [
                    {
                        "user": "Alice",
                        "comment": "Essential reading!",
                        "rating": 5,
                        "date": "2026-03-30T00:00:00"
                    }
                ]
            }
        ]
        
        print("\n1. Saving book collection...")
        with safe_file_write(demo_file) as f:
            json.dump(books, f, indent=2, ensure_ascii=False)
        print(f"   ✅ Saved {len(books)} books")
        
        print("\n2. Loading book collection...")
        with safe_file_read(demo_file) as f:
            if f is None:
                print("   ❌ File not found")
                loaded_books = []
            else:
                loaded_books = json.load(f)
                print(f"   ✅ Loaded {len(loaded_books)} books")
        
        print("\n3. Book details:")
        for i, book in enumerate(loaded_books, 1):
            status = "📗" if book['read'] else "📕"
            review_count = len(book['reviews'])
            print(f"   {status} {book['title']} by {book['author']} ({book['year']})")
            if review_count > 0:
                print(f"      ⭐ {review_count} review(s)")
        
        print("\n✅ Demo 4 completed - Real-world usage verified\n")
    finally:
        # Cleanup
        if os.path.exists(demo_file):
            os.unlink(demo_file)


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("CONTEXT MANAGER DEMONSTRATION")
    print("=" * 60)
    print("\nThis demo showcases the context managers in storage.py:")
    print("  • safe_file_write() - Atomic writes with error recovery")
    print("  • safe_file_read() - Graceful missing file handling")
    print()
    
    try:
        demo_safe_file_write()
        demo_safe_file_write_error_recovery()
        demo_safe_file_read()
        demo_real_world_usage()
        
        print("=" * 60)
        print("ALL DEMOS COMPLETED SUCCESSFULLY! 🎉")
        print("=" * 60)
        print("\nKey Takeaways:")
        print("  ✅ Atomic writes prevent data corruption")
        print("  ✅ Automatic cleanup on errors")
        print("  ✅ Graceful handling of missing files")
        print("  ✅ Clean, readable code")
        print("  ✅ Resource management guaranteed")
        print()
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        raise


if __name__ == "__main__":
    main()
