import os


def update_extends_statement(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()

                if "{% extends 'mailing/base.html' %}" in content:
                    content = content.replace("{% extends 'mailing/base.html' %}", "{% extends 'base.html' %}")
                    with open(file_path, 'w') as f:
                        f.write(content)
                    print(f"Updated: {file_path}")


template_directory = 'mailing/templates/mailing'
update_extends_statement(template_directory)
