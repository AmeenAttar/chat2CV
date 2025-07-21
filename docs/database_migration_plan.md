# Database Migration Plan: String to Integer Template IDs

## 🚨 **Critical Database Changes Required**

### **1. Resume Table Migration**
```sql
-- Current schema (problematic)
template_id = Column(String(100), nullable=False)  # e.g., "professional", "modern"

-- New schema (optimal)
template_id = Column(Integer, nullable=False)  # e.g., 1, 2, 3, 4, 5
```

**Migration Steps:**
1. Add new `template_id_int` column
2. Migrate existing data: `"1"` → `1`, `"2"` → `2`, etc.
3. Update foreign key constraints
4. Drop old `template_id` column
5. Rename `template_id_int` to `template_id`

### **2. Template Table Migration**
```sql
-- Current schema
template_id = Column(String(100), unique=True, nullable=False)  # e.g., "professional"

-- New schema
template_id = Column(Integer, unique=True, nullable=False)  # e.g., 1
```

**Migration Steps:**
1. Update template records with integer IDs
2. Update unique constraints
3. Update indexes for performance

### **3. ResumeSection Table Migration**
```sql
-- Any template_id references need updating
template_id = Column(Integer, nullable=False)  # If exists
```

## 📋 **Migration Script**

```python
# migration_script.py
from app.services.template_registry import TemplateID

def migrate_template_ids():
    """Migrate string template IDs to integer IDs"""
    
    # Mapping of old string IDs to new integer IDs
    template_mapping = {
        "1": TemplateID.PROFESSIONAL,  # 1
        "2": TemplateID.MODERN,        # 2
        "3": TemplateID.CREATIVE,      # 3
        "4": TemplateID.MINIMALIST,    # 4
        "5": TemplateID.EXECUTIVE,     # 5
        "professional": TemplateID.PROFESSIONAL,
        "modern": TemplateID.MODERN,
        "creative": TemplateID.CREATIVE,
        "minimalist": TemplateID.MINIMALIST,
        "executive": TemplateID.EXECUTIVE,
    }
    
    # Update Resume table
    for old_id, new_id in template_mapping.items():
        db.execute(
            "UPDATE resumes SET template_id = %s WHERE template_id = %s",
            (new_id, old_id)
        )
    
    # Update Template table
    for old_id, new_id in template_mapping.items():
        db.execute(
            "UPDATE templates SET template_id = %s WHERE template_id = %s",
            (new_id, old_id)
        )
```

## 🔧 **Files That Need Updating**

### **1. Database Models (✅ COMPLETED)**
- ✅ `app/models/database_models.py` - Updated Resume and Template models
- ✅ `app/models/resume.py` - Updated Pydantic models

### **2. API Endpoints (✅ COMPLETED)**
- ✅ `app/main.py` - Updated request models

### **3. Database Service (✅ COMPLETED)**
- ✅ `app/services/database_service.py` - Updated method signatures

### **4. Services That Need Updating (✅ COMPLETED)**
- ✅ `app/services/template_service.py` - Replaced with template registry
- ✅ `app/services/template_aware_parser.py` - Updated to use integer IDs
- ✅ `app/services/ai_agent.py` - Updated to use template registry
- ✅ `app/services/llama_index_rag.py` - Updated template ID handling
- ✅ `app/services/rag_service.py` - Updated template ID handling
- ✅ `app/services/simple_rag.py` - Updated template ID handling

### **5. Database Setup (✅ COMPLETED)**
- ✅ `setup_database.py` - Updated template creation with integer IDs
- ✅ `alembic/versions/d55918878800_initial_database_schema.py` - Updated migration

### **6. Tests (✅ COMPLETED)**
- ✅ `test_backend.py` - Updated test data and assertions
- ✅ `test_template_aware_parser.py` - Updated test cases
- ✅ `test_template_registry.py` - Already updated ✅

## 📝 **Specific Method Updates Required**

### **Template Service Replacement**
```python
# OLD: app/services/template_service.py
def get_template_by_id(self, template_id: str) -> TemplateInfo:

# NEW: Use template registry instead
from app.services.template_registry import TemplateRegistry
registry = TemplateRegistry()
theme = registry.get_theme_by_id(template_id: int)
```

### **Template-Aware Parser Updates**
```python
# OLD: app/services/template_aware_parser.py
def parse_education_output(self, raw_output: str, template_id: str) -> Optional[Education]:

# NEW: 
def parse_education_output(self, raw_output: str, template_id: int) -> Optional[Education]:
```

### **AI Agent Updates**
```python
# OLD: app/services/ai_agent.py
def generate_section(self, template_id: str, section_name: str, ...):

# NEW:
def generate_section(self, template_id: int, section_name: str, ...):
```

### **Database Setup Updates**
```python
# OLD: setup_database.py
templates = [
    {"template_id": "professional", "name": "Professional", ...},
    {"template_id": "modern", "name": "Modern", ...},
]

# NEW:
templates = [
    {"template_id": 1, "name": "Professional", ...},
    {"template_id": 2, "name": "Modern", ...},
]
```

## ⚠️ **Breaking Changes**

### **API Endpoints**
- All API endpoints using `template_id: str` need updating
- Frontend calls need to send integers instead of strings
- Database queries need updating

### **Data Validation**
- Pydantic models need updating
- Type hints need changing
- Validation logic needs updating

### **Tests**
- All tests using string template IDs need updating
- Mock data needs updating
- Test assertions need updating

## 🚀 **Migration Priority Order**

1. **HIGH PRIORITY**: Update remaining services (template_service, template_aware_parser, ai_agent) ✅ **COMPLETED**
2. **HIGH PRIORITY**: Update database setup and migrations ✅ **COMPLETED**
3. **MEDIUM PRIORITY**: Update all tests ✅ **COMPLETED**
4. **LOW PRIORITY**: Update documentation and examples

## 🔄 **Backward Compatibility**

**Option 1: Gradual Migration**
- Keep both string and integer support temporarily
- Add conversion methods
- Deprecate string IDs over time

**Option 2: Hard Cutover**
- Update everything at once
- Requires coordinated deployment
- Higher risk but cleaner

**Recommended: Option 1** for production systems with existing data.

## ✅ **MIGRATION STATUS: COMPLETE**

All pending changes have been successfully implemented:

- ✅ **Database Models**: Updated to use integer template IDs
- ✅ **API Endpoints**: Updated request models 
- ✅ **Database Service**: Updated method signatures
- ✅ **Pydantic Models**: Updated type hints
- ✅ **Template Service**: Replaced with template registry
- ✅ **Template-Aware Parser**: Updated to use integer IDs
- ✅ **AI Agent**: Updated to use template registry
- ✅ **RAG Services**: Updated template ID handling
- ✅ **Database Setup**: Updated template creation
- ✅ **Tests**: Updated all test data and assertions
- ✅ **Database Migration**: Updated schema to use integer IDs

**Next Steps:**
1. Run database migrations: `alembic upgrade head`
2. Test the updated system with integer template IDs
3. Update any frontend code to send integer template IDs
4. Monitor for any remaining string template ID references 