#!/usr/bin/env python3
"""
Quick Memory Inspector - Run this in Cursor terminal to see memory contents
Usage: python src/quick_memory_inspect.py
"""

import os
import sys
import json
from pathlib import Path

# Set up the same environment as the demo
project_root = Path(__file__).parent.parent  # Go up from src/ to LL3/
storage_dir = project_root / "storage"  # LL3/storage
os.environ["CREWAI_STORAGE_DIR"] = str(storage_dir)

def quick_inspect():
    """Quick inspection of memory files"""
    print("🔍 Quick Memory Inspector")
    print("=" * 60)
    print(f"📁 Storage Directory: {storage_dir}")
    
    if not storage_dir.exists():
        print("❌ Storage directory doesn't exist. Run the demo first!")
        return
    
    # List all files
    files = list(storage_dir.iterdir())
    print(f"\n📄 Files ({len(files)} total):")
    for file in files:
        if file.is_file():
            size = file.stat().st_size
            print(f"   📄 {file.name} ({size:,} bytes)")
        else:
            print(f"   📁 {file.name}/")
    
    # Try to inspect SQLite databases
    print(f"\n📊 SQLite Databases:")
    
    # Long-term Memory
    ltm_db = storage_dir / "long_term_memory_storage.db"
    if ltm_db.exists():
        print(f"   📄 long_term_memory_storage.db")
        try:
            import sqlite3
            conn = sqlite3.connect(str(ltm_db))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"      📋 {table_name}: {count} records")
                
                # Show sample data for small tables
                if count > 0 and count <= 5:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                    rows = cursor.fetchall()
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    for i, row in enumerate(rows):
                        row_dict = dict(zip(columns, row))
                        # Truncate long values for display
                        display_row = {}
                        for k, v in row_dict.items():
                            if isinstance(v, str) and len(v) > 100:
                                display_row[k] = v[:100] + "..."
                            else:
                                display_row[k] = v
                        print(f"         Row {i+1}: {display_row}")
            
            conn.close()
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # Task Outputs
    task_db = storage_dir / "latest_kickoff_task_outputs.db"
    if task_db.exists():
        print(f"   📄 latest_kickoff_task_outputs.db")
        try:
            import sqlite3
            conn = sqlite3.connect(str(task_db))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"      📋 {table_name}: {count} records")
            
            conn.close()
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # Try to inspect ChromaDB
    print(f"\n🧠 ChromaDB Collections:")
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(storage_dir))
        collections = client.list_collections()
        
        if collections:
            for collection in collections:
                try:
                    count = collection.count()
                    collection_id = str(collection.id)[:8] if hasattr(collection.id, '__getitem__') else str(collection.id)[:8]
                    print(f"   📁 {collection.name} ({collection_id}...): {count} documents")
                    
                    if count > 0:
                        # Get sample documents
                        results = collection.get(limit=2, include=['documents', 'metadatas'])
                        if results['documents']:
                            print(f"      Sample documents:")
                            for i, doc in enumerate(results['documents']):
                                display_doc = doc[:150] + "..." if len(doc) > 150 else doc
                                print(f"         Doc {i+1}: {display_doc}")
                        
                        if results['metadatas']:
                            print(f"      Sample metadata:")
                            for i, meta in enumerate(results['metadatas']):
                                print(f"         Meta {i+1}: {meta}")
                except Exception as e:
                    print(f"   ❌ Error reading {collection.name}: {e}")
        else:
            print("   📄 No ChromaDB collections found")
    
    except ImportError:
        print("   ⚠️  ChromaDB not available")
    except Exception as e:
        print(f"   ❌ ChromaDB error: {e}")
    
    print(f"\n" + "=" * 60)
    print("💡 Run this script after conversations to see memory updates")
    print("🌐 Or visit http://localhost:8002/memory-inspect for JSON API")

if __name__ == "__main__":
    quick_inspect()
