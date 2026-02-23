import markdown
import os

def main():
    # Create the output directory
    if not os.path.exists("docs"):
        os.makedirs("docs")

    # Get all markdown files
    markdown_files = [f for f in os.listdir('.') if f.endswith('.md')]

    # Convert each markdown file to HTML
    for md_file in markdown_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            text = f.read()
            html = markdown.markdown(text)
            
            # Create a full HTML document
            html_content = f"""<!DOCTYPE html>
<html>
<head>
<title>{os.path.basename(md_file)}</title>
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
<div class="container">
{html}
</div>
</body>
</html>"""

            # Save the HTML file
            html_file = os.path.join("docs", os.path.splitext(md_file)[0] + '.html')
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

    # Create the index.html file
    with open(os.path.join("docs", "index.html"), 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html><html><head><title>Bitacora Red Team</title>')
        f.write('<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">')
        f.write('</head><body><div class="container">')
        f.write('<h1>Bitacora Red Team</h1><ul>')
        for md_file in markdown_files:
            html_file = os.path.splitext(md_file)[0] + '.html'
            f.write(f'<li><a href="{html_file}">{os.path.splitext(md_file)[0]}</a></li>')
        f.write('</ul></div></body></html>')

if __name__ == "__main__":
    main()
