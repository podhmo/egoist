import typing as t
from openapi.runtime import App

app = App()


class Article:
    title: str
    content: str


@app.post("/api/articles", metadata={"tags": ["xxx"]})
def create_article(article: Article) -> t.List[Article]:
    pass
