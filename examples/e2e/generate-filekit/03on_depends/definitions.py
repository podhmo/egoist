from egoist.app import App, SettingsDict, parse_args

settings: SettingsDict = {"rootdir": "output", "here": __file__}
app = App(settings)

app.include("egoist.directives.define_file")


@app.define_file("egoist.generators.filekit:walk", suffix=".json")
def season(*, source="input/season.csv") -> None:
    import csv
    import json
    from egoist.generators.filekit import runtime

    with runtime.create_file() as wf:
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
