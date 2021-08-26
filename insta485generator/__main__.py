"""Insta485 package initializer."""
import json
import sys
import shutil
import pathlib
import click
import jinja2

@click.command()
@click.option('-o', '--output', help="Output directory.")
@click.option('-v', '--verbose', is_flag=True, help="Print more output.")
@click.argument('INPUT_DIR')
def main(output, verbose, input_dir):
    """Insta485 package initializer."""
    input_dir = pathlib.Path(input_dir)
    if input_dir.exists() is False:
        print("No input dir")
        sys.exit(1)
    static_dir = input_dir/"static"
    if output is None:
        output_dir = input_dir/"html"
    else:
        output_dir = pathlib.Path(output)
    if static_dir.exists():
        if output_dir.exists() is True:
            print("Output dir exist")
            sys.exit(1)
        shutil.copytree(static_dir, output_dir)
        if verbose:
            print("Copied", static_dir, "->", output_dir)
    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(input_dir/"templates")),
        autoescape=jinja2.select_autoescape(['html', 'xml']),
    )
    records = json.load(open(input_dir/"config.json"))
    for datas in records:
        url = datas['url'].lstrip("/")
        template_html = datas['template']
        context = datas['context']
        output_path = output_dir/url/"index.html"
        des_dir = output_dir/url
        if output_path.exists() is True:
            print("Already exist")
            sys.exit(1)
        if des_dir.exists() is False:
            des_dir.mkdir(parents=True)
        template = template_env.get_template(template_html)
        data = template.render(context)
        output_path.write_text(data)
        if verbose:
            print("Rendered", template_html, "->", output_path)


if __name__ == "__main__":
    main()
    sys.exit(0)
