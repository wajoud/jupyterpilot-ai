import inspect
import json

class SchemaIntrospector:
    """Introspects the IPython namespace for data-related objects."""
    
    def __init__(self, shell):
        self.shell = shell

    def get_context(self):
        """Scan globals and return a string describing data objects found."""
        context_parts = []
        
        # We iterate over a copy of the user namespace to avoid 'size changed during iteration' errors
        user_ns = self.shell.user_ns.copy()
        
        for name, obj in user_ns.items():
            if name.startswith("_"):
                continue
                
            # Pandas DataFrame
            if self._is_pandas_df(obj):
                context_parts.append(self._describe_pandas(name, obj))
                
            # SQLAlchemy Engine
            elif self._is_sqlalchemy_engine(obj):
                context_parts.append(self._describe_sql(name, obj))
                
            # MongoDB Database
            elif self._is_mongodb_db(obj):
                context_parts.append(self._describe_mongo(name, obj))
                
        if not context_parts:
            return ""
            
        return "\n--- Data Schema Context ---\n" + "\n\n".join(context_parts)

    def _is_pandas_df(self, obj):
        try:
            import pandas as pd
            return isinstance(obj, pd.DataFrame)
        except ImportError:
            return False

    def _describe_pandas(self, name, df):
        cols = list(df.columns)
        dtypes = df.dtypes.to_dict()
        sample = df.head(2).to_json(orient='records')
        return f"Pandas DataFrame '{name}':\n- Columns: {cols}\n- Dtypes: {dtypes}\n- Sample Data: {sample}"

    def _is_sqlalchemy_engine(self, obj):
        try:
            from sqlalchemy.engine import Engine
            return isinstance(obj, Engine)
        except ImportError:
            return False

    def _describe_sql(self, name, engine):
        try:
            from sqlalchemy import inspect as sqla_inspect
            inspector = sqla_inspect(engine)
            tables_info = []
            for table_name in inspector.get_table_names()[:5]: # Limit to 5 tables
                columns = [c['name'] for c in inspector.get_columns(table_name)]
                tables_info.append(f"  - Table '{table_name}': columns {columns}")
            
            info_str = "\n".join(tables_info)
            return f"SQLAlchemy Engine '{name}':\n{info_str}"
        except Exception as e:
            return f"SQLAlchemy Engine '{name}' found, but failed to inspect: {e}"

    def _is_mongodb_db(self, obj):
        try:
            from pymongo.database import Database
            return isinstance(obj, Database)
        except ImportError:
            return False

    def _describe_mongo(self, name, db):
        try:
            collections = db.list_collection_names()[:5] # Limit to 5 collections
            col_info = []
            for col_name in collections:
                # 1. Fetch latest up to 20 docs to gather comprehensive schema
                try:
                    cursor = db[col_name].find().sort('_id', -1).limit(20)
                    docs = list(cursor)
                except Exception:
                    # Fallback if sorting by _id fails
                    cursor = db[col_name].find().limit(20)
                    docs = list(cursor)
                
                # 2. Extract all unique keys across these 20 docs
                schema_keys = set()
                for doc in docs:
                    schema_keys.update(doc.keys())
                schema_str = ", ".join(sorted(list(schema_keys))) if schema_keys else "None"
                
                # 3. Retrieve index information
                try:
                    indexes = db[col_name].index_information()
                    indexed_fields = []
                    for idx_name, idx_info in indexes.items():
                        if 'key' in idx_info:
                            keys = [k[0] for k in idx_info['key']]
                            indexed_fields.append(f"{idx_name}({','.join(keys)})")
                    index_str = ", ".join(indexed_fields) if indexed_fields else "None"
                except Exception:
                    index_str = "Unknown"

                # 4. Use the latest document as a single sample
                sample = docs[0] if docs else None
                # Remove _id if it's an ObjectId for JSON serialization
                if sample and '_id' in sample:
                    sample['_id'] = str(sample['_id'])
                    
                col_info.append(
                    f"  - Collection '{col_name}':\n"
                    f"    - Schema Keys: {schema_str}\n"
                    f"    - Indexes: {index_str}\n"
                    f"    - Sample Doc: {json.dumps(sample) if sample else '{}'}"
                )
            
            info_str = "\n".join(col_info)
            return f"MongoDB Database '{name}':\n{info_str}"
        except Exception as e:
            return f"MongoDB Database '{name}' found, but failed to inspect: {e}"
