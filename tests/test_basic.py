def test_dummy():
    # Simple test to confirm pipeline works
    assert 1 + 1 == 2

def test_imports():
    import os, importlib

    python_files = [f for f in os.listdir('.') if f.endswith('.py')]

    for file in python_files:
        module = file.replace('.py', '')
        importlib.import_module(module)
