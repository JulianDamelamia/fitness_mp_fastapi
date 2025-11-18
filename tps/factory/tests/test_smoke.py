import sys
import os

# Add the parent directory of 'simple_factory', 'factory_method', and 'abstract_factory' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    import simple_factory.main as s
    import factory_method.main as fm
    import abstract_factory.main as af
    assert callable(s.main) and callable(fm.main) and callable(af.main)

if __name__ == "__main__":
    test_imports()