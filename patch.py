#!/usr/bin/env python3
"""
Script to patch OpenWebUI for monitoring integration
"""
import sys
import re

def patch_main_py(filepath):
    """Add monitoring router registration to main.py"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Add import if not already there
    if 'from open_webui.routers import (' in content and 'monitoring' not in content:
        content = content.replace(
            'from open_webui.routers import (',
            'from open_webui.routers import (\n    monitoring,'
        )
    
    # Add router registration if not already there
    if 'include_router(monitoring.router' not in content:
        # Find a good spot after existing include_router calls
        pattern = r'(app\.include_router\([^)]+\))\n'
        matches = list(re.finditer(pattern, content))
        if matches:
            # Insert after the last include_router call
            last_match = matches[-1]
            insert_pos = last_match.end()
            router_line = 'app.include_router(monitoring.router, prefix="/api/admin/monitoring", tags=["monitoring"])\n'
            content = content[:insert_pos] + router_line + content[insert_pos:]
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✅ Patched {filepath}")

def patch_index_html(filepath):
    """Add script injection to index.html"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    if 'inject-sidebar.js' not in content:
        content = content.replace(
            '</html>',
            '<script async src="/api/admin/monitoring/inject-sidebar.js"></script>\n</html>'
        )
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✅ Patched {filepath}")

if __name__ == '__main__':
    try:
        patch_main_py('/app/backend/open_webui/main.py')
        patch_index_html('/app/build/index.html')
        print("\n✅ All patches applied successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
