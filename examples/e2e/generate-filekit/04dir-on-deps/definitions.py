from egoist.app import create_app, SettingsDict, parse_args

settings: SettingsDict = {"rootdir": "", "here": __file__}
app = create_app(settings)

app.include("egoist.directives.define_dir")


@app.define_dir("egoist.generators.dirkit:walk")
def output(*, source="input/season.csv") -> None:
    import csv
    import json
    from egoist.generators.dirkit import runtime

    with runtime.create_file("seasons.json", depends_on=[source]) as wf:
        name_list = []
        ja_list = []

        with open(source) as rf:
            for row in csv.DictReader(rf):
                name_list.append(row["name"])
                ja_list.append(row["ja"])

        data = {
            "definitions": {
                "season": {"type": "string", "enum": name_list, "x-ja-enum": ja_list}
            }
        }
        json.dump(data, wf, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    for argv in parse_args(sep="-"):
        app.run(argv)
