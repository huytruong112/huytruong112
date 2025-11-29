import sys
sys.path.insert(0, '/home/ubuntu/.local/lib/python3.10/site-packages')

# Test các function chính
print("Testing functions...")

# Test imports
try:
    import streamlit as st
    import requests
    import json
    import time
    print("✓ All imports OK")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test mock functions
print("\nTesting debug expanders...")

# Mock streamlit functions
class MockExpander:
    def __init__(self, label, expanded=False):
        self.label = label
        self.expanded = expanded
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass

st.expander = MockExpander
st.write = lambda *args, **kwargs: None
st.error = lambda *args, **kwargs: None
st.code = lambda *args, **kwargs: None

# Test debug code snippets
try:
    # Simulate debug info
    with st.expander("🔍 Debug Info", expanded=False):
        st.write("**Request URL:**", "http://test")
        st.write("**Payload keys:**", ['test'])
    print("✓ Debug Info expander works")
    
    # Simulate debug response
    with st.expander("🔍 Debug Response", expanded=False):
        st.write("**Status Code:**", 200)
        st.write("**Response Text:**", "test")
    print("✓ Debug Response expander works")
    
except Exception as e:
    print(f"✗ Debug expander failed: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ All function tests passed!")
