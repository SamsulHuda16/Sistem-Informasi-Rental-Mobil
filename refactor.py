import os
import re

tpl_dir = 'administrator/templates/administrator'

files_to_skip = ['base_admin.html', 'dashboard.html', 'pengaturan.html']

for filename in os.listdir(tpl_dir):
    if filename in files_to_skip or not filename.endswith('.html'):
        continue
        
    filepath = os.path.join(tpl_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Extract Title
    title_match = re.search(r'<title>(.*?)</title>', content)
    title = title_match.group(1) if title_match else "Dashboard"
    
    # Extract Container Content
    # We look for <div class="container"> ... </div></body>
    container_match = re.search(r'<div class="container">(.*?)</div>\s*</body>', content, re.DOTALL)
    if not container_match:
        # try without strict closing
        container_match = re.search(r'<div class="container">(.*)', content, re.DOTALL)
        if not container_match:
            print(f"Skipping {filename}, no container found.")
            continue
            
    inner_content = container_match.group(1)
    
    # Clean up inner content
    # Remove 'Kembali ke Dashboard'
    inner_content = re.sub(r'<a href="\{% url \'admin_dashboard\' %\}"[^>]*>.*?</a>', '', inner_content, flags=re.DOTALL)
    
    # Replace buttons and tables for Bootstrap 5
    inner_content = re.sub(r'<table\b[^>]*>', '<div class="table-responsive"><table class="table table-bordered table-striped mt-3 align-middle">', inner_content)
    inner_content = inner_content.replace('</table>', '</table></div>')
    
    inner_content = re.sub(r'class="btn"', 'class="btn btn-primary"', inner_content)
    inner_content = re.sub(r'class="edit"', 'class="btn btn-sm btn-warning text-dark"', inner_content)
    inner_content = re.sub(r'class="hapus"', 'class="btn btn-sm btn-danger"', inner_content)
    inner_content = re.sub(r'class="btn-danger"', 'class="btn btn-danger"', inner_content)
    inner_content = re.sub(r'class="btn-success"', 'class="btn btn-success"', inner_content)
    
    # Forms inside container usually have unstyled inputs, add form-control
    inner_content = re.sub(r'<input\b(?![^>]*type="file"|type="submit")[^>]*>', lambda m: m.group(0).replace('>', ' class="form-control mb-3">') if 'class=' not in m.group(0) else m.group(0), inner_content)
    inner_content = re.sub(r'<select\b[^>]*>', lambda m: m.group(0).replace('>', ' class="form-control mb-3">') if 'class=' not in m.group(0) else m.group(0), inner_content)
    
    # Submit buttons
    inner_content = re.sub(r'<button type="submit"[^>]*>', lambda m: m.group(0).replace('>', ' class="btn btn-primary">') if 'class=' not in m.group(0) else m.group(0), inner_content)
    
    new_content = f"""{{% extends 'administrator/base_admin.html' %}}

{{% block title %}}{title}{{% endblock %}}

{{% block content %}}
<div class="card shadow-sm border-0">
    <div class="card-body p-4">
        {inner_content.strip()}
    </div>
</div>
{{% endblock %}}
"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Refactored {filename}")
